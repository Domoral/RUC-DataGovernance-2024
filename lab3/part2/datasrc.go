package main

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


type DataSrc struct {
	DOI				string `json:"DOI"`  // 数据资源的标识
	NAME			string `json:"NAME"`  // 数据资源的名称
	OWNER			string `json:"OWNER"`  // 数据资源的拥有者
	PRICE			string `json:"PRICE"`  // 数据资源的价格
	DATA_LOCATION	string `json:"DATA_LOCATION"`  // 数据资源的位置
}

// company own DataSrc_s
