use pyo3::prelude::*;
use pyo3::types::PyDict;
use solana_client::rpc_client::RpcClient;
use solana_sdk::instruction::{AccountMeta, Instruction};
use solana_sdk::message::Message;
use solana_sdk::pubkey::Pubkey;
use solana_sdk::signature::{read_keypair_file, Keypair, Signer};
use solana_sdk::system_program;
use solana_sdk::transaction::Transaction;
use solana_sdk::commitment_config::CommitmentConfig;
use borsh::{BorshDeserialize, BorshSerialize};
use anchor_client::{Client, Cluster};
use anchor_lang::{AccountDeserialize, Discriminator};
use std::rc::Rc;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::env;
use std::str::FromStr;

// The IDL is bundled so account and instruction metadata travel with the extension.
const IDL_JSON: &str = include_str!("../../idl.json");

#[derive(BorshDeserialize, BorshSerialize, Serialize, Deserialize, Debug)]
struct SimpleAccount {
    pub key: u64,
    pub value: u64,
}

#[derive(Debug, Clone)]
struct GigEscrow {
    client: Pubkey,
    freelancer: Pubkey,
    oracle: Pubkey,
    amount: u64,
    job_id: String,
    status: String,
    escrow_bump: u8,
    vault_bump: u8,
    deadline: i64,
}

impl Discriminator for GigEscrow {
    const DISCRIMINATOR: [u8; 8] = [28, 152, 50, 155, 169, 194, 206, 20];
}

impl AccountDeserialize for GigEscrow {
    fn try_deserialize(buf: &mut &[u8]) -> anchor_lang::Result<Self> {
        let decoded = decode_gig_escrow(buf).map_err(|_| anchor_lang::error::ErrorCode::AccountDidNotDeserialize)?;
        *buf = &[];
        Ok(decoded)
    }

    fn try_deserialize_unchecked(buf: &mut &[u8]) -> anchor_lang::Result<Self> {
        let mut bytes = Self::discriminator().to_vec();
        bytes.extend_from_slice(buf);
        let decoded = decode_gig_escrow(&bytes).map_err(|_| anchor_lang::error::ErrorCode::AccountDidNotDeserialize)?;
        *buf = &[];
        Ok(decoded)
    }
}

fn py_error<E: std::fmt::Display>(kind: fn(String) -> PyErr, error: E) -> PyErr {
    kind(error.to_string())
}

fn idl_value() -> Result<Value, String> {
    serde_json::from_str(IDL_JSON).map_err(|error| format!("Bundled IDL is invalid: {error}"))
}

fn idl_discriminator(section: &str, name: &str) -> Result<[u8; 8], String> {
    let idl = idl_value()?;
    let entries = idl
        .get(section)
        .and_then(Value::as_array)
        .ok_or_else(|| format!("IDL section '{section}' is missing"))?;
    let entry = entries
        .iter()
        .find(|entry| entry.get("name").and_then(Value::as_str) == Some(name))
        .ok_or_else(|| format!("'{name}' is missing from IDL section '{section}'"))?;
    let values = entry
        .get("discriminator")
        .and_then(Value::as_array)
        .ok_or_else(|| format!("'{name}' has no discriminator in the IDL"))?;
    if values.len() != 8 {
        return Err(format!("'{name}' discriminator must contain 8 bytes"));
    }
    let mut output = [0u8; 8];
    for (index, value) in values.iter().enumerate() {
        output[index] = value
            .as_u64()
            .filter(|byte| *byte <= u8::MAX as u64)
            .ok_or_else(|| format!("invalid discriminator byte at index {index}"))?
            as u8;
    }
    Ok(output)
}

fn read_pubkey(data: &[u8], cursor: &mut usize) -> Result<Pubkey, String> {
    let end = cursor.checked_add(32).ok_or_else(|| "account data overflow".to_string())?;
    if end > data.len() {
        return Err("account data ended while reading a public key".to_string());
    }
    let key = Pubkey::new_from_array(data[*cursor..end].try_into().map_err(|_| "invalid public key bytes")?);
    *cursor = end;
    Ok(key)
}

fn read_u64(data: &[u8], cursor: &mut usize) -> Result<u64, String> {
    let end = cursor.checked_add(8).ok_or_else(|| "account data overflow".to_string())?;
    if end > data.len() {
        return Err("account data ended while reading u64".to_string());
    }
    let value = u64::from_le_bytes(data[*cursor..end].try_into().map_err(|_| "invalid u64 bytes")?);
    *cursor = end;
    Ok(value)
}

fn read_i64(data: &[u8], cursor: &mut usize) -> Result<i64, String> {
    let end = cursor.checked_add(8).ok_or_else(|| "account data overflow".to_string())?;
    if end > data.len() {
        return Err("account data ended while reading i64".to_string());
    }
    let value = i64::from_le_bytes(data[*cursor..end].try_into().map_err(|_| "invalid i64 bytes")?);
    *cursor = end;
    Ok(value)
}

fn read_u8(data: &[u8], cursor: &mut usize) -> Result<u8, String> {
    if *cursor >= data.len() {
        return Err("account data ended while reading u8".to_string());
    }
    let value = data[*cursor];
    *cursor += 1;
    Ok(value)
}

fn read_borsh_string(data: &[u8], cursor: &mut usize) -> Result<String, String> {
    let length = read_u32(data, cursor)? as usize;
    if length > 32 {
        return Err("GigEscrow job_id exceeds the 32-byte IDL limit".to_string());
    }
    let end = cursor.checked_add(length).ok_or_else(|| "account data overflow".to_string())?;
    if end > data.len() {
        return Err("account data ended while reading job_id".to_string());
    }
    let value = std::str::from_utf8(&data[*cursor..end])
        .map_err(|_| "job_id is not valid UTF-8".to_string())?
        .to_string();
    *cursor = end;
    Ok(value)
}

fn read_u32(data: &[u8], cursor: &mut usize) -> Result<u32, String> {
    let end = cursor.checked_add(4).ok_or_else(|| "account data overflow".to_string())?;
    if end > data.len() {
        return Err("account data ended while reading u32".to_string());
    }
    let value = u32::from_le_bytes(data[*cursor..end].try_into().map_err(|_| "invalid u32 bytes")?);
    *cursor = end;
    Ok(value)
}

fn decode_gig_escrow(data: &[u8]) -> Result<GigEscrow, String> {
    let discriminator = idl_discriminator("accounts", "GigEscrow")?;
    if data.len() < 8 || data[..8] != discriminator {
        return Err("account discriminator does not identify GigEscrow".to_string());
    }
    let mut cursor = 8usize;
    let client = read_pubkey(data, &mut cursor)?;
    let freelancer = read_pubkey(data, &mut cursor)?;
    let oracle = read_pubkey(data, &mut cursor)?;
    let amount = read_u64(data, &mut cursor)?;
    let job_id = read_borsh_string(data, &mut cursor)?;
    let status = match read_u8(data, &mut cursor)? {
        0 => "Pending",
        1 => "Completed",
        2 => "Cancelled",
        value => return Err(format!("unknown JobStatus discriminant {value}")),
    }
    .to_string();
    let escrow_bump = read_u8(data, &mut cursor)?;
    let vault_bump = read_u8(data, &mut cursor)?;
    let deadline = read_i64(data, &mut cursor)?;
    Ok(GigEscrow {
        client,
        freelancer,
        oracle,
        amount,
        job_id,
        status,
        escrow_bump,
        vault_bump,
        deadline,
    })
}

fn dict_from_escrow(py: Python<'_>, escrow: &GigEscrow) -> PyResult<PyObject> {
    let dict = PyDict::new_bound(py);
    dict.set_item("status", &escrow.status)?;
    dict.set_item("amount", escrow.amount)?;
    dict.set_item("jobId", &escrow.job_id)?;
    dict.set_item("client", escrow.client.to_string())?;
    dict.set_item("freelancer", escrow.freelancer.to_string())?;
    dict.set_item("oracle", escrow.oracle.to_string())?;
    Ok(dict.to_object(py))
}

fn fetch_gig_escrow(rpc_url: &str, address: &str) -> Result<GigEscrow, String> {
    let client = RpcClient::new(rpc_url.to_string());
    let pubkey = Pubkey::from_str(address).map_err(|error| format!("Invalid address: {error}"))?;
    let account = client.get_account(&pubkey).map_err(|error| format!("RPC Error: {error}"))?;
    decode_gig_escrow(&account.data)
}

fn fetch_gig_escrow_with_anchor_client(rpc_url: &str, program_id: &str, address: &str) -> Result<GigEscrow, String> {
    let program_key = Pubkey::from_str(program_id).map_err(|error| format!("Invalid program_id: {error}"))?;
    let account_key = Pubkey::from_str(address).map_err(|error| format!("Invalid address: {error}"))?;
    let websocket_url = if rpc_url.starts_with("https://") {
        rpc_url.replacen("https://", "wss://", 1)
    } else if rpc_url.starts_with("http://") {
        rpc_url.replacen("http://", "ws://", 1)
    } else {
        return Err("RPC URL must start with http:// or https://".to_string());
    };
    let provider = Client::new_with_options(
        Cluster::Custom(rpc_url.to_string(), websocket_url),
        Rc::new(Keypair::new()),
        CommitmentConfig::confirmed(),
    );
    let program = provider.program(program_key).map_err(|error| format!("Anchor client error: {error}"))?;
    program.account::<GigEscrow>(account_key).map_err(|error| format!("Anchor account error: {error}"))
}

#[pyfunction]
fn get_balance(rpc_url: String, address: String) -> PyResult<u64> {
    let client = RpcClient::new(rpc_url);
    let pubkey = Pubkey::from_str(&address)
        .map_err(|error| py_error(PyErr::new::<pyo3::exceptions::PyValueError, _>, format!("Invalid address: {error}")))?;
    client
        .get_balance(&pubkey)
        .map_err(|error| py_error(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>, format!("RPC Error: {error}")))
}

#[pyfunction]
fn get_account_data(rpc_url: String, address: String) -> PyResult<Vec<u8>> {
    let client = RpcClient::new(rpc_url);
    let pubkey = Pubkey::from_str(&address)
        .map_err(|error| py_error(PyErr::new::<pyo3::exceptions::PyValueError, _>, format!("Invalid address: {error}")))?;
    let account = client
        .get_account(&pubkey)
        .map_err(|error| py_error(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>, format!("RPC Error: {error}")))?;
    Ok(account.data)
}

#[pyfunction]
fn deserialize_simple_account(data: Vec<u8>) -> PyResult<PyObject> {
    let account = SimpleAccount::try_from_slice(&data)
        .map_err(|error| py_error(PyErr::new::<pyo3::exceptions::PyValueError, _>, format!("Deserialization Error: {error}")))?;
    Python::with_gil(|py| {
        let dict = PyDict::new_bound(py);
        dict.set_item("key", account.key)?;
        dict.set_item("value", account.value)?;
        Ok(dict.to_object(py))
    })
}

#[pyfunction]
fn solana_deserialize_gig_escrow(data: Vec<u8>) -> PyResult<PyObject> {
    let escrow = decode_gig_escrow(&data)
        .map_err(|error| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Deserialization Error: {error}")))?;
    Python::with_gil(|py| dict_from_escrow(py, &escrow))
}

#[pyfunction]
fn anchor_fetch_account(rpc_url: String, _program_id: String, address: String, account_type: String) -> PyResult<PyObject> {
    if account_type != "GigEscrow" {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Unsupported account type: {account_type}")));
    }
    let escrow = fetch_gig_escrow_with_anchor_client(&rpc_url, &_program_id, &address)
        .map_err(|error| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(error))?;
    Python::with_gil(|py| dict_from_escrow(py, &escrow))
}

fn instruction_dict(py: Python<'_>, method: &str, program_id: &str, escrow_address: &str, signer_key: &str) -> PyResult<PyObject> {
    let discriminator = idl_discriminator("instructions", method)
        .map_err(|error| PyErr::new::<pyo3::exceptions::PyValueError, _>(error))?;
    let dict = PyDict::new_bound(py);
    dict.set_item("type", method)?;
    dict.set_item("program_id", program_id)?;
    dict.set_item("escrow_address", escrow_address)?;
    dict.set_item("authority", signer_key)?;
    dict.set_item("data", discriminator.to_vec())?;
    Ok(dict.to_object(py))
}

#[pyfunction]
fn anchor_build_release_ix(program_id: String, escrow_address: String, oracle_pubkey: String) -> PyResult<PyObject> {
    Python::with_gil(|py| instruction_dict(py, "release_payment", &program_id, &escrow_address, &oracle_pubkey))
}

#[pyfunction]
fn anchor_build_cancel_ix(program_id: String, escrow_address: String, oracle_pubkey: String) -> PyResult<PyObject> {
    Python::with_gil(|py| instruction_dict(py, "cancel_job", &program_id, &escrow_address, &oracle_pubkey))
}

struct InstructionSpec {
    method: String,
    program_id: Pubkey,
    escrow_address: Pubkey,
    signer: Pubkey,
}

fn get_string(dict: &Bound<'_, PyDict>, key: &str) -> PyResult<String> {
    dict.get_item(key)?
        .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("instruction is missing '{key}'")))?
        .extract::<String>()
}

fn parse_instruction(py: Python<'_>, instruction: &PyObject) -> PyResult<InstructionSpec> {
    let dict = instruction
        .bind(py)
        .downcast::<PyDict>()
        .map_err(|_| PyErr::new::<pyo3::exceptions::PyTypeError, _>("instruction must be a dict"))?;
    let method = get_string(dict, "type")?;
    let program_id = Pubkey::from_str(&get_string(dict, "program_id")?)
        .map_err(|error| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid program_id: {error}")))?;
    let escrow_address = Pubkey::from_str(&get_string(dict, "escrow_address")?)
        .map_err(|error| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid escrow_address: {error}")))?;
    let signer = Pubkey::from_str(&get_string(dict, "authority")?)
        .map_err(|error| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid authority: {error}")))?;
    Ok(InstructionSpec { method, program_id, escrow_address, signer })
}

fn build_real_instruction(rpc_url: &str, spec: &InstructionSpec) -> Result<Instruction, String> {
    let escrow = fetch_gig_escrow(rpc_url, &spec.escrow_address.to_string())?;
    let vault = Pubkey::find_program_address(
        &[b"vault", escrow.client.as_ref(), escrow.job_id.as_bytes()],
        &spec.program_id,
    )
    .0;
    let discriminator = idl_discriminator("instructions", &spec.method)?;
    let accounts = match spec.method.as_str() {
        "release_payment" => vec![
            AccountMeta::new_readonly(spec.signer, true),
            AccountMeta::new(escrow.freelancer, false),
            AccountMeta::new(escrow.client, false),
            AccountMeta::new(spec.escrow_address, false),
            AccountMeta::new(vault, false),
            AccountMeta::new_readonly(system_program::id(), false),
        ],
        "cancel_job" => vec![
            AccountMeta::new_readonly(spec.signer, true),
            AccountMeta::new(escrow.client, false),
            AccountMeta::new(spec.escrow_address, false),
            AccountMeta::new(vault, false),
            AccountMeta::new_readonly(system_program::id(), false),
        ],
        other => return Err(format!("unsupported instruction type '{other}'")),
    };
    Ok(Instruction { program_id: spec.program_id, accounts, data: discriminator.to_vec() })
}

#[pyfunction]
fn anchor_simulate_tx(rpc_url: String, instruction: PyObject) -> PyResult<PyObject> {
    let spec = Python::with_gil(|py| parse_instruction(py, &instruction))?;
    let ix = build_real_instruction(&rpc_url, &spec)
        .map_err(|error| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(error))?;
    let client = RpcClient::new(rpc_url);
    let blockhash = client
        .get_latest_blockhash()
        .map_err(|error| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("RPC Error: {error}")))?;
    let message = Message::new(&[ix], Some(&spec.signer));
    let mut transaction = Transaction::new_unsigned(message);
    transaction.message.recent_blockhash = blockhash;
    let result = client
        .simulate_transaction(&transaction)
        .map_err(|error| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Simulation RPC Error: {error}")))?;
    Python::with_gil(|py| {
        let dict = PyDict::new_bound(py);
        dict.set_item("success", result.value.err.is_none())?;
        dict.set_item("logs", result.value.logs.unwrap_or_default())?;
        if let Some(error) = result.value.err {
            dict.set_item("error", format!("{error:?}"))?;
        }
        Ok(dict.to_object(py))
    })
}

#[pyfunction]
fn anchor_send_tx(rpc_url: String, instruction: PyObject, keypair_env_var: String) -> PyResult<String> {
    if !rpc_url.contains("devnet") {
        return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("anchor_send_tx blocked in strict mode: only devnet RPC URLs are allowed"));
    }
    if env::var("PYMINI_ALLOW_SEND").unwrap_or_default() != "1" {
        return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("anchor_send_tx blocked in strict mode: PYMINI_ALLOW_SEND must equal 1"));
    }
    let keypair_path = env::var(&keypair_env_var).map_err(|_| {
        PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("keypair environment variable '{keypair_env_var}' is not set"))
    })?;
    let keypair = read_keypair_file(&keypair_path).map_err(|error| {
        PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("failed to read keypair file: {error}"))
    })?;
    let spec = Python::with_gil(|py| parse_instruction(py, &instruction))?;
    if spec.signer != keypair.pubkey() {
        return Err(PyErr::new::<pyo3::exceptions::PyPermissionError, _>("keypair does not match the instruction signer"));
    }
    let ix = build_real_instruction(&rpc_url, &spec)
        .map_err(|error| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(error))?;
    let client = RpcClient::new(rpc_url);
    let blockhash = client
        .get_latest_blockhash()
        .map_err(|error| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("RPC Error: {error}")))?;
    let transaction = Transaction::new_signed_with_payer(&[ix], Some(&keypair.pubkey()), &[&keypair], blockhash);
    let signature = client
        .send_and_confirm_transaction(&transaction)
        .map_err(|error| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Send RPC Error: {error}")))?;
    Ok(signature.to_string())
}

#[pymodule]
fn pymini_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_balance, m)?)?;
    m.add_function(wrap_pyfunction!(get_account_data, m)?)?;
    m.add_function(wrap_pyfunction!(deserialize_simple_account, m)?)?;
    m.add_function(wrap_pyfunction!(solana_deserialize_gig_escrow, m)?)?;
    m.add_function(wrap_pyfunction!(anchor_fetch_account, m)?)?;
    m.add_function(wrap_pyfunction!(anchor_build_release_ix, m)?)?;
    m.add_function(wrap_pyfunction!(anchor_build_cancel_ix, m)?)?;
    m.add_function(wrap_pyfunction!(anchor_simulate_tx, m)?)?;
    m.add_function(wrap_pyfunction!(anchor_send_tx, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn idl_contains_expected_gig_escrow_discriminator() {
        assert_eq!(idl_discriminator("accounts", "GigEscrow").unwrap(), [28, 152, 50, 155, 169, 194, 206, 20]);
    }
}
