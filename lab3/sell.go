/*
Copyright IBM Corp. 2016 All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

		 http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package main

//WARNING - this chaincode's ID is hard-coded in chaincode_example04 to illustrate one way of
//calling chaincode from a chaincode. If this example is modified, chaincode_example04.go has
//to be modified as well with the new ID of chaincode_example02.
//chaincode_example05 show's how chaincode ID can be passed in as a parameter instead of
//hard-coding.

import (
	"fmt"
	"strconv"
	"time"
	"encoding/json"
	"github.com/hyperledger/fabric/core/chaincode/shim"
	pb "github.com/hyperledger/fabric/protos/peer"
)

// SimpleChaincode example simple Chaincode implementation
type SimpleChaincode struct {
}

type SellInfo struct {
	TX_ID				string `json:"TX_ID"`
	SEND_DATE			string `json:"NODE_DATE"`
	REPAYMENT_DATE		string `json:"REPAYMENT_DATE"`
	AMOUNT				string `json:"AMOUNT"`
	INTEREST			string `json:"INTEREST"`
	STATUS				string `json:"STATUS"`
	SELLER				string `json:"SELLER"`
	BUYER				string `json:"BUYER"`
}

// 链码实例化： 输入 company1, init_val1, company2, init_val2
func (t *SimpleChaincode) Init(stub shim.ChaincodeStubInterface) pb.Response {
	fmt.Println("ex02 Init")

	_, args := stub.GetFunctionAndParameters()
	var A, B string
	var Aval, Bval int
	var err error

	if len(args) != 4 {
		return shim.Error("Incorrect number of arguments. Expecting 4")
	}

	
	A = args[0]
	Aval, err = strconv.Atoi(args[1])
	if err != nil {
		return shim.Error("Expecting integer value for asset holding")
	}
	B = args[2]
	Bval, err = strconv.Atoi(args[3])
	if err != nil {
		return shim.Error("Expecting integer value for asset holding")
	}
	fmt.Printf("Aval = %d, Bval = %d\n", Aval, Bval)

	err = stub.PutState(A, []byte(strconv.Itoa(Aval)))
	if err != nil {
		return shim.Error(err.Error())
	}

	err = stub.PutState(B, []byte(strconv.Itoa(Bval)))
	if err != nil {
		return shim.Error(err.Error())
	}

	return shim.Success(nil)
}

func (t *SimpleChaincode) Invoke(stub shim.ChaincodeStubInterface) pb.Response {
	fmt.Println("ex02 Invoke")
	function, args := stub.GetFunctionAndParameters()
	if function == "check" {
		return t.check(stub, args)
	} else if function == "create" {
		return t.create(stub, args)
	} else if function == "query" {
		return t.query(stub, args)
	} else if function == "payment" {
		return t.payment(stub, args)
	}

	return shim.Error("Invalid invoke function name. Expecting \"create\" \"check\" \"query\" \"payment\"")
}

// Transaction makes payment of X units from A to B
// input: TXID, SEND_DATE, AMOUNT, SELLER, BUYER
// function: 创建交易记录 from seller to buyer
func (t *SimpleChaincode) create(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	if len(args) != 5 {
		return shim.Error("Incorrect number of arguments. Expecting 5")
	}
	fmt.Println("create is running 000")
	optInfoDatas, _ := stub.GetState(args[0])
	if optInfoDatas != nil {
		return shim.Error("this tx has exist.")
	}
	fmt.Println("create is running 001")
	var stuff = SellInfo{TX_ID: args[0], SEND_DATE: args[1], REPAYMENT_DATE: "", AMOUNT: args[2], INTEREST: "", STATUS: "1", SELLER: args[3], BUYER: args[4]}
	stuffBytes, err := json.Marshal(stuff)
	if err != nil {
		return shim.Error(err.Error())
	}
	fmt.Println("create is running 002")
	err = stub.PutState(args[0], stuffBytes)
	if err != nil {
		return shim.Error(err.Error())
	}
	fmt.Println("create is running 003")

	return shim.Success(nil)
}

func (t *SimpleChaincode) check(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	if len(args) != 1 {
		return shim.Error("Incorrect number of arguments. Expecting 1")
	}

	tx, _ := stub.GetState(args[0])

	if tx == nil {
		return shim.Error("Failed to get Data. The Tx does not exist!")
	}

	var SellInfos SellInfo
	err := json.Unmarshal(tx, &SellInfos)
	if err != nil {
		return shim.Error(err.Error())
	}

	SellInfos.STATUS = "2"

	targetInfo, err := json.Marshal(SellInfos)
	if err != nil {
		return shim.Error(err.Error())
	}
	stub.PutState(args[0], targetInfo)

	return shim.Success(nil)
}

// query callback representing the query of a chaincode
// 查找交易记录 
// 输入：
// if interest 为空， 则输入 TXID, SEND_DATE
// if interest 不为空， 则输入 ?
// return 交易记录
func (t *SimpleChaincode) query(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	if len(args) < 1 {
		return shim.Error("Incorrect number of arguments. Expecting name of the person to query")
	}

	TxBytes, err := stub.GetState(args[0])
	if err != nil {
		jsonResp := "{\"Error\":\"Failed to get state for " + args[0] + "\"}"
		return shim.Error(jsonResp)
	}

	if TxBytes == nil {
		jsonResp := "{\"Error\":\"Nil amount for " + args[0] + "\"}"
		return shim.Error(jsonResp)
	}

	var SellInfos SellInfo
	err1 := json.Unmarshal(TxBytes, &SellInfos)
	if err1 != nil {
		return shim.Error(err1.Error())
	}

	interest := SellInfos.INTEREST

	if interest == "" {
		if len(args) != 2 {
			return shim.Error("Incorrect number of arguments.")
		}
		payable_Date, _ := time.Parse("2006-01-02", SellInfos.SEND_DATE)
		payable_Date = payable_Date.Add(30 * 24 * time.Hour)

		pay_Date, _ := time.Parse("2006-01-02", args[1])

		if payable_Date.Before(pay_Date) {
			interest = "2000"
		}
	}

	jsonResp := "{\"TX_ID\":\"" + SellInfos.TX_ID + "\",\"SEND_DATE\":\"" + SellInfos.SEND_DATE + "\",\"AMOUNT\":\"" + SellInfos.AMOUNT + "\",\"INTEREST\":\"" + interest +
		"\",\"STATUS\":\"" + SellInfos.STATUS + "\",\"SELLER\":\"" + SellInfos.SELLER + "\",\"BUYER\":\"" + SellInfos.BUYER + "\",\"REPAYMENT_DATE\":\"" + SellInfos.REPAYMENT_DATE + "\"}"
	fmt.Printf("Query Response:%s\n", jsonResp)
	return shim.Success([]byte(jsonResp))
}

func (t *SimpleChaincode) payment(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	if len(args) != 3 {
		return shim.Error("Incorrect number of argsments.")
	}

	TxBytes, err := stub.GetState(args[0])
	if err != nil {
		jsonResp := "{\"Error\":\"Failed to get state for " + args[0] + "\"}"
		return shim.Error(jsonResp)
	}

	if TxBytes == nil {
		jsonResp := "{\"Error\":\"Nil amount for " + args[0] + "\"}"
		return shim.Error(jsonResp)
	}

	var SellInfos SellInfo
	err1 := json.Unmarshal(TxBytes, &SellInfos)
	if err1 != nil {
		return shim.Error(err1.Error())
	}

	payable_Date, _ := time.Parse("2006-01-02", SellInfos.SEND_DATE)
	payable_Date = payable_Date.Add(30 * 24 * time.Hour)

	pay_Date, _ := time.Parse("2006-01-02", args[1])

	interest := 0
	if payable_Date.Before(pay_Date) {
		interest = 2000
	}

	amount, err := strconv.Atoi(SellInfos.AMOUNT)
	if err != nil {
		jsonResp := "{\"Error\":\" amount is error\"}"
		return shim.Error(jsonResp)
	}

	pay, err := strconv.Atoi(args[2])
	if err != nil {
		jsonResp := "{\"Error\":\" pay value is error\"}"
		return shim.Error(jsonResp)
	}

	if pay < amount + interest {
		jsonResp := "{\"Error\":\" Insufficient amount.\"}"
		return shim.Error(jsonResp)
	}

	SellInfos.INTEREST = strconv.Itoa(interest)
	SellInfos.STATUS = "3"
	SellInfos.REPAYMENT_DATE = args[1]

	targetInfo, err := json.Marshal(SellInfos)
	if err !=  nil {
		return shim.Error(err.Error())
	}
	stub.PutState(args[0], targetInfo)

	return shim.Success(nil)
}

func main() {
	err := shim.Start(new(SimpleChaincode))
	if err != nil {
		fmt.Printf("Error starting Simple chaincode: %s", err)
	}
}
