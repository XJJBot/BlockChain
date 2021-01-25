小组成员：谢俊杰-18340181



该大作业是基于FISCO BCOS v2.7.1 文档的python-sdk完成的，需要部署相应的python sdk并与`code`文件夹中的文件合并，同时前端部分基于pyqt5模块完成。



代码说明：

`code/deploy.py`--部署智能合约，并获得相应合约部署的地址

`code/main.py`--运行供应链金融平台软件制品（需要将代码中的address更改为上述合约地址）



运行说明：

1、搭建私有链、加入新节点并启动所有节点

```shell
bash nodes/127.0.0.1/start_all.sh
```

2、`python deploy.py`

3、`python main.py`

