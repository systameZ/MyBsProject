# 毕设
前端使用bootstrap + jquery的方案，使用开源gentelella进行布局和交互实现。后端使用django + saltstack + mysql，调试阶段使用django自带的服务端进行调试。前端穿插使用ajax与后端进行交互，以达到练习使用django模板标签和ajax的目的。后端的django与saltstack主机间的通讯采用salt-api，即在主控端开启salt-api，web后端通过HTTPS的POST的方式进行管理和功能使用。后端的数据存储使用Mysql数据库，数据库的调用通过django的models下orm的方式进行数据的访问、修改等操作
