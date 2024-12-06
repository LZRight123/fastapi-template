import random
import string


# 生成一个随机用户名
def generate_random_username(length:int=5) -> str:
    """ 
    生成随机用户名字符串
    """
    # 可以包含在用户名中的字符集合
    characters = string.ascii_letters + string.digits  # 包含字母和数字
    # 生成随机用户名
    random_username = "".join(random.choices(characters, k=length))
    username = f"胃之书用户{random_username}"
    return username
    
# 生成随机4位数纯数字验证码
def generate_random_sms_code(length:int=4) -> str:
    """
    生成随机4位数纯数字验证码
    """
    # 生成随机验证码
    code = random.randint(1000, 9999)
    return str(code)

# 生成随机5位字母和数字组成的邀请码，字母全部大写,且保证唯一
def generate_random_invite_code(length:int=5) -> str:
    """
    生成随机5位字母和数字组成的邀请码，字母全部大写,且保证唯一
    
    注意: 这个函数本身不能保证生成的邀请码唯一性。调用方需要:
    1. 在数据库中建立唯一索引
    2. 使用事务和重试机制处理冲突
    3. 或者维护一个已使用邀请码的集合来确保唯一性
    """
    # 生成随机邀请码
    code = random.choices(string.ascii_uppercase + string.digits, k=length)
    return "".join(code)
