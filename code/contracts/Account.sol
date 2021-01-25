pragma solidity ^0.4.25;
pragma experimental ABIEncoderV2;
import "./Table.sol";

contract Account {
    event RegisterResult(int256 count, string company_name);
    event SelectResult(int256 count, string[] from_str, string[] to_str, int256[] total_amount_int, int256[] cur_amount_int, string[] ddl_str);
    event InsertResult(int256 count, string from_str, string to_str, int256 total_amount_int, int256 cur_amount_int, string ddl_str);
    event UpdateResult(int256 count, string from_str, string to_str, int256 total_amount_int, int256 cur_amount_int, string ddl_str);
    event RemoveResult(int256 count, string from_str, string to_str, int256 total_amount_int, int256 cur_amount_int, string ddl_str);
    
    constructor() public {
        createCompanyTable();
        createReceiptTable();
    }
    
    function createCompanyTable() private {
        TableFactory tf = TableFactory(0x1001);
        //账款单据表, key: status, field: name
        // |  （主键）     |  状态      |
        // |---------------|------------|
        // |     name      | status     |
        // |---------------|------------|
        tf.createTable("t_company", "name", "status");
    }
    
    function createReceiptTable() private {
        TableFactory tf = TableFactory(0x1001);
        //账款单据表, key: status, field: from(string), to(string), total_amount(int256), cur_amount(int256), deadline(string)
        // |  （主键）     |  源头企业  |  去向企业  |  总金额        |  当前金额    |  还款日期  |
        // |---------------|------------|------------|----------------|--------------|------------|
        // |     key       |  from      |  to        |  total_amount  |  cur_amount  |  deadline  |
        // |---------------|------------|------------|----------------|--------------|------------|
        tf.createTable("t_receipt", "key", "from, to, total_amount, cur_amount, deadline");
    }
    
    function openTable(string t_name) private returns(Table) {
        TableFactory tf = TableFactory(0x1001);
        Table t = tf.openTable(t_name);
        return t;
    } 
    
    //为企业在链上注册
    function insert_company(string company_name) public returns(int256) {
        int256 ret = select_company(company_name);
        if (ret == 0) {
            Table t = openTable("t_company");
            Entry e = t.newEntry();
            e.set("status", "valid");
            e.set("name", company_name);
            int256 count = t.insert(company_name, e);
            emit RegisterResult(count, company_name);
            return count;
        }
        //企业已存在
        else {
            emit RegisterResult(0, "failed");
            return 0;
        }
    }
    
    //查询企业是否在链上
    function select_company(string company_name) public returns(int256) {
        Table t = openTable("t_company");
        Entries es = t.select(company_name, t.newCondition());
        if (uint256(es.size()) == 0) {
            return 0;
        } 
        else {
            return 1;
        }
    }
    
    
    //提取出单据信息
    function extract(Entries es1) public
    returns(string[] memory, string[] memory, int256[] memory, int256[] memory, string[] memory) {
        string[] memory from_list = new string[](uint256(es1.size()));
        string[] memory to_list = new string[](uint256(es1.size()));
        int256[] memory tot_amo_list = new int256[](uint256(es1.size()));
        int256[] memory cur_amo_list = new int256[](uint256(es1.size()));
        string[] memory ddl_list = new string[](uint256(es1.size()));
        
        for (int i = 0; i < es1.size(); i++) {
            Entry e = es1.get(i);
            from_list[uint256(i)] = e.getString("from");
            to_list[uint256(i)] = e.getString("to");
            tot_amo_list[uint256(i)] = e.getInt("total_amount");
            cur_amo_list[uint256(i)] = e.getInt("cur_amount");
            ddl_list[uint256(i)] = e.getString("deadline");
        }
        emit SelectResult(es1.size(), from_list, to_list, tot_amo_list, cur_amo_list, ddl_list);
        return (from_list, to_list, tot_amo_list, cur_amo_list, ddl_list);
    }
    
    //查询与该企业相关的账款单据
    function select(string company_name, int256 from_or_to) public 
    returns(string[] memory, string[] memory, int256[] memory, int256[] memory, string[] memory) {
        Table t = openTable("t_receipt");
        Condition c1 = t.newCondition();
        //查询签发的单据
        if (from_or_to == 1) {
            c1.EQ("from", company_name);
        }
        //查询得到的单据
        else if (from_or_to == 2) {
            c1.EQ("to", company_name);
        }
        
        Entries es1 = t.select("valid", c1);
        return extract(es1);
    }
    
    //插入账款单据
    function insert(string from_str, string to_str, int256 total_amount_int, int256 cur_amount_int, string ddl_str) public
    returns(int256) {
        Table t = openTable("t_receipt");
        Entry e = t.newEntry();
        e.set("key", "valid");
        e.set("from", from_str);
        e.set("to", to_str);
        e.set("total_amount", total_amount_int);
        e.set("cur_amount", cur_amount_int);
        e.set("deadline", ddl_str);
        int256 count = t.insert("valid", e);
        emit InsertResult(count, from_str, to_str, total_amount_int, cur_amount_int, ddl_str);
        return count;
    }
    
    //根据from和to找到并更新账款单据
    function update(string from_str, string to_str, int256 total_amount_int, int256 cur_amount_int, string ddl_str) public
    returns(int256) {
        Table t = openTable("t_receipt");
        Entry e = t.newEntry();
        e.set("total_amount", total_amount_int);
        e.set("cur_amount", cur_amount_int);
        Condition c = t.newCondition();
        c.EQ("from", from_str);
        c.EQ("to", to_str);
        c.EQ("deadline", ddl_str);
        int256 count = t.update("valid", e, c);
        emit UpdateResult(count, from_str, to_str, total_amount_int, cur_amount_int, ddl_str);
        return count;
    }
    
    //移除账款单据
    function remove(string from_str, string to_str, int256 total_amount_int, int256 cur_amount_int, string ddl_str) public
    returns(int256) {
        Table t = openTable("t_receipt");
        Condition c = t.newCondition();
        c.EQ("from", from_str);
        c.EQ("to", to_str);
        c.EQ("total_amount", total_amount_int);
        c.EQ("cur_amount", cur_amount_int);
        c.EQ("deadline", ddl_str);
        int256 count = t.remove("valid", c);
        emit RemoveResult(count, from_str, to_str, total_amount_int, cur_amount_int, ddl_str);
        return count;
    }
    
    //还款
    function pay(string from_str, string to_str, int256 total_amount_int, int256 cur_amount_int, string ddl_str) public returns(int256) {
        int256 count = remove(from_str, to_str, total_amount_int, cur_amount_int, ddl_str);
        return count;
    }
    
    //融资
    function finance(string from_str, int256 total_amount_int, string ddl_str) public returns(int256) {
        int256 ret = select_company(to_str);
        if (ret == 0) {
            emit InsertResult(0, from_str, "bank", total_amount_int, total_amount_int, ddl_str);
            return 0;
        }
        int256 count = insert(from_str, "bank", total_amount_int, total_amount_int, ddl_str);
        return count;
    }
    
    //签订应收账款单据
    function sign(string from_str, string to_str, int256 total_amount_int, string ddl_str) public returns(int256) {
        //双方企业是否存在
        int256 ret = select_company(from_str);
        if (ret == 0) {
            emit InsertResult(0, from_str, to_str, total_amount_int, total_amount_int, ddl_str);
            return 0;
        }
        ret = select_company(to_str);
        if (ret == 0) {
            emit InsertResult(0, from_str, to_str, total_amount_int, total_amount_int, ddl_str);
            return 0;
        }
        int256 count = insert(from_str, to_str, total_amount_int, total_amount_int, ddl_str);
        return count;
    }
    
    //转让
    function transfer(string from_str, string to_str, string to_to_str, int256 total_amount_int, int256 cur_amount_int, int256 transfer_amount, string ddl_str) public 
    returns(int256) {
        //双方企业是否存在
        int256 ret = select_company(from_str);
        if (ret == 0) {
            emit InsertResult(0, from_str, to_str, total_amount_int, cur_amount_int, ddl_str);
            return 0;
        }
        ret = select_company(to_str);
        if (ret == 0) {
            emit InsertResult(0, from_str, to_str, total_amount_int, cur_amount_int, ddl_str);
            return 0;
        }
        
        int256 ret_code = 0;
        int256 cur = cur_amount_int - transfer_amount;
        //转让金额大于剩余金额
        if (cur < 0) {
            ret_code = -1;
            return ret_code;
        }
        //转让后剩余金额为0则移除
        else if (cur == 0) {
            remove(from_str, to_str, total_amount_int, cur_amount_int, ddl_str);
        }
        else {
            update(from_str, to_str, total_amount_int, cur, ddl_str);
        }
        ret_code = insert(from_str, to_to_str, transfer_amount, transfer_amount, ddl_str);
        return ret_code;
    }
}















