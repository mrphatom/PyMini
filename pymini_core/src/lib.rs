use pyo3::prelude::*;
use solana_client::rpc_client::RpcClient;
use solana_sdk::pubkey::Pubkey;
use std::str::FromStr;
use borsh::{BorshDeserialize, BorshSerialize};
use serde::{Serialize, Deserialize};

#[derive(BorshDeserialize, BorshSerialize, Serialize, Deserialize, Debug)]
struct SimpleAccount {
    pub key: u64,
    pub value: u64,
}

#[pyfunction]
fn get_balance(rpc_url: String, address: String) -> PyResult<u64> {
    let client = RpcClient::new(rpc_url);
    let pubkey = Pubkey::from_str(&address)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid address: {}", e)))?;
    
    let balance = client.get_balance(&pubkey)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("RPC Error: {}", e)))?;
    
    Ok(balance)
}

#[pyfunction]
fn get_account_data(rpc_url: String, address: String) -> PyResult<Vec<u8>> {
    let client = RpcClient::new(rpc_url);
    let pubkey = Pubkey::from_str(&address)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid address: {}", e)))?;
    
    let account = client.get_account(&pubkey)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("RPC Error: {}", e)))?;
    
    Ok(account.data)
}

#[pyfunction]
fn deserialize_simple_account(data: Vec<u8>) -> PyResult<PyObject> {
    let account = SimpleAccount::try_from_slice(&data)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Deserialization Error: {}", e)))?;
    
    Python::with_gil( |py| {
        let dict = pyo3::types::PyDict::new_bound(py);
        dict.set_item("key", account.key)?;
        dict.set_item("value", account.value)?;
        Ok(dict.to_object(py))
    })
}

/// A Python module implemented in Rust.
#[pymodule]
fn pymini_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_balance, m)?)?;
    m.add_function(wrap_pyfunction!(get_account_data, m)?)?;
    m.add_function(wrap_pyfunction!(deserialize_simple_account, m)?)?;
    Ok(())
}
