package main

import (
	"encoding/json"
	"fmt"
	"strconv"
	"time"

	"github.com/hyperledger/fabric/core/chaincode/shim"
	pb "github.com/hyperledger/fabric/protos/peer"
)

// SimpleChaincode example simple Chaincode implementation
type SimpleChaincode struct {
}

type DataSrc struct {
	DOI           string `json:"DOI"`           // 数据资源的标识
	NAME          string `json:"NAME"`          // 数据资源的名称
	OWNER         string `json:"OWNER"`         // 数据资源的拥有者
	PRICE         string `json:"PRICE"`         // 数据资源的价格
	DATA_LOCATION string `json:"DATA_LOCATION"` // 数据资源的位置
}

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
	function, args := stub.GetFunctionAndParameters()
	fmt.Printf("Invoking function: %s\n", function)

	switch function {
	case "create":
		return t.create(stub, args)
	case "alter":
		return t.alter(stub, args)
	case "delete":
		return t.delete(stub, args)
	case "query":
		return t.query(stub, args)
	case "payment":
		return t.payment(stub, args)
	}

	return shim.Error("Invalid function name. Expecting 'create', 'alter', 'delete', 'query', or 'payment'")
}

func (t *SimpleChaincode) create(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	if len(args) != 5 {
		return shim.Error("Incorrect number of arguments. Expecting 5")
	}

	doi := args[0]
	name := args[1]
	owner := args[2]
	price := args[3]
	location := args[4]

	dataSrc := &DataSrc{
		DOI:           doi,
		NAME:          name,
		OWNER:         owner,
		PRICE:         price,
		DATA_LOCATION: location,
	}

	dataSrcBytes, err := json.Marshal(dataSrc)
	if err != nil {
		return shim.Error("Error marshaling data source")
	}

	err = stub.PutState(doi, dataSrcBytes)
	if err != nil {
		return shim.Error("Error saving data source")
	}

	return shim.Success(nil)
}

func (t *SimpleChaincode) alter(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	if len(args) != 5 {
		return shim.Error("Incorrect number of arguments. Expecting 5")
	}

	doi := args[0]
	name := args[1]
	owner := args[2]
	price := args[3]
	location := args[4]

	dataSrcBytes, err := stub.GetState(doi)
	if err != nil {
		return shim.Error("Failed to get data source")
	}
	if dataSrcBytes == nil {
		return shim.Error("Data source does not exist")
	}

	dataSrc := &DataSrc{}
	err = json.Unmarshal(dataSrcBytes, dataSrc)
	if err != nil {
		return shim.Error("Error unmarshaling data source")
	}

	dataSrc.NAME = name
	dataSrc.OWNER = owner
	dataSrc.PRICE = price
	dataSrc.DATA_LOCATION = location

	dataSrcBytes, err = json.Marshal(dataSrc)
	if err != nil {
		return shim.Error("Error marshaling updated data source")
	}

	err = stub.PutState(doi, dataSrcBytes)
	if err != nil {
		return shim.Error("Error saving updated data source")
	}

	return shim.Success(nil)
}

func (t *SimpleChaincode) delete(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	if len(args) != 1 {
		return shim.Error("Incorrect number of arguments. Expecting 1")
	}

	doi := args[0]

	err := stub.DelState(doi)
	if err != nil {
		return shim.Error("Failed to delete data source")
	}

	return shim.Success(nil)
}

func (t *SimpleChaincode) query(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	if len(args) != 1 {
		return shim.Error("Incorrect number of arguments. Expecting 1")
	}

	doi := args[0]

	dataSrcBytes, err := stub.GetState(doi)
	if err != nil {
		return shim.Error("Failed to get data source")
	}
	if dataSrcBytes == nil {
		return shim.Error("Data source does not exist")
	}

	return shim.Success(dataSrcBytes)
}

func (t *SimpleChaincode) payment(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	if len(args) != 3 {
		return shim.Error("Incorrect number of arguments. Expecting 3")
	}

	buyer := args[0]
	doi := args[1]
	amount := args[2]

	dataSrcBytes, err := stub.GetState(doi)
	if err != nil {
		return shim.Error("Failed to get data source")
	}
	if dataSrcBytes == nil {
		return shim.Error("Data source does not exist")
	}

	dataSrc := &DataSrc{}
	err = json.Unmarshal(dataSrcBytes, dataSrc)
	if err != nil {
		return shim.Error("Error unmarshaling data source")
	}

	if amount != dataSrc.PRICE {
		return shim.Error("Incorrect payment amount")
	}

	// 在实际应用中，这里应该有转账操作
	// 为简化起见，我们只是记录交易

	transaction := fmt.Sprintf("Buyer: %s, DataSrc: %s, Amount: %s, Time: %s", buyer, doi, amount, time.Now().String())
	err = stub.PutState(buyer+"-"+doi, []byte(transaction))
	if err != nil {
		return shim.Error("Failed to record transaction")
	}

	return shim.Success([]byte(dataSrc.DATA_LOCATION))
}

func main() {
	err := shim.Start(new(SimpleChaincode))
	if err != nil {
		fmt.Printf("Error starting Simple chaincode: %s", err)
	}
}