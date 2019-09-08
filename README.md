<p>
<img height="200" src="./misc/awp.png">
</p>

# awp quotesys
quotesys 是期货行情服务器，负责从数据接口采集tick数据，然后根据既定的规则生成需要的K线数据。

安装：

1、git clone https://github.com/pctp/quotesys

2、pip install -r requirements.txt

3、安装 redis 数据库。

4、目前的程序是在python 2.7下开发的，经过简单改动就支持python 3.6 （穿透式接口pyctp在python 3.7下面编译暂时有问题，要用python 3.7 的可以用vnpy的接口或者tqsdk）


使用：

1、执行 python ctp_data_collect_engine.py   负责收集tick数据，目前支持ctp穿透式行情接口，tqsdk接口。

2、执行 python data_arrange_engine.py  负责生成K线数据

3、执行 python main.py   提供K线数据服务

4、在程序中获取数据 请使用 function.py 的load_data_from_server函数

5、历史tick数据导入，请使用  	push_to_queue.py 目前支持从tb导出的tick数据，或者tqsdk下载的tick数据。


系统目前在ubuntu　18.04, majaro 18　测试通过。暂时不支持windows.

windows 的用户可以使用本地文件的版本 	data_sewing_machine.py 即可。
