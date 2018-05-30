# 需要安装的模块, 使用python3
pip install tornado munch tormysql pymysql pycrypto tornado_smtp phantomas

# 预定义参数
{random_mobile} 随机手机号
{random_email}  随机email
{timestamp}     时间戳
{datetime}      当前时间, 格式: %Y-%m-%d %H:%M:%S
{datetime_int}  当前时间, 格式: %Y%m%d%H%M%S
{date}          当前日期, 格式: %Y-%m-%d
{date_int}      当前日期, 格式: %Y%m%d

# 系统关联参数
{cookie}=response_headers.Set-Cookie      获取cookie
{body}=response_body 获取完整响应body

# 关联参数支持int和float类型转换
{id}=int(data.id)
{total}=float(data.[0].total)

# 关联参数支持正则表达式取值
{headers}=response_headers./.*/      获取所有响应headers
{body}=/测试字符串(\d+),/      取出【测试字符串】与【,】之间的数字