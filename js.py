import json
import os
import time
import platform
from datetime import datetime
import hashlib
import shutil
import re

# 系统常量
USERS_FILE = "users.json"  # 用户数据库
ADMIN_USERNAME = "金子涵JL"
ADMIN_PASSWORD = "jzh17364268762"
MAX_HISTORY = 5  # 最大保存的历史路径数量

# 用户数据结构
DEFAULT_USER = {
    "username": "",
    "password_hash": "",
    "role": "user",  # user/subadmin/admin
    "private_folder": "",
    "created_by": "",  # 记录创建者
    "email": "",  # 新增邮箱字段用于找回密码
    "security_question": "",  # 安全问题
    "security_answer": ""  # 安全答案
}

# 全局变量
current_user = None
config = {}

def clear_screen():
    """清屏函数，兼容不同操作系统"""
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def init_user_system():
    """初始化用户系统"""
    # 如果用户数据库不存在，则创建
    if not os.path.exists(USERS_FILE):
        # 创建默认管理员账户
        admin_user = DEFAULT_USER.copy()
        admin_user["username"] = ADMIN_USERNAME
        admin_user["password_hash"] = hash_password(ADMIN_PASSWORD)
        admin_user["role"]#极速模式建议关闭 = "admin"
        admin_user["private_folder"] = f"user_{ADMIN_USERNAME}"
        admin_user["created_by"] = "system"
        
        # 创建用户数据库
        with open(USERS_FILE, "w") as f:
            json.dump({"users": [admin_user]}, f, indent=4)
        
        # 创建管理员私有文件夹
        os.makedirs(admin_user["private_folder"], exist_ok=True)
        print(f"已创建管理员账户: {ADMIN_USERNAME}")
    else:
        # 修复现有用户数据：确保所有用户都有role字段
        try:
            with open(USERS_FILE, "r") as f:
                users_db = json.load(f)
            
            fixed = False
            for user in users_db["users"]:
                # 特别处理管理员账户
                if user["username"] == ADMIN_USERNAME:
                    # 如果是管理员账户，确保角色是admin
                    if user.get("role") != "admin":
                        user["role"] = "admin"
                        fixed = True
                # 确保其他用户有role字段
                elif "role" not in user:
                    user["role"] = "user"
                    fixed = True
                # 确保其他字段也存在
                for key in DEFAULT_USER:
                    if key not in user:
                        user[key] = DEFAULT_USER[key]
                        fixed = True
            
            if fixed:
                with open(USERS_FILE, "w") as f:
                    json.dump(users_db, f, indent=4)
                print("已修复用户数据")
        except Exception as e:
            print(f"用户数据库修复失败: {e}")

def hash_password(password):
    """使用SHA256哈希密码"""
    return hashlib.sha256(password.encode()).hexdigest()

def user_login():
    """用户登录"""
    global current_user
    
    while True:
        clear_screen()
        print("\n======= 用户登录 =======")
        username = input("用户名: ").strip()
        password = input("密码: ").strip()
        
        if not username or not password:
            print("用户名和密码不能为空")
            time.sleep(1)
            continue
        
        # 加载用户数据库
        try:
            with open(USERS_FILE, "r") as f:
                users_db = json.load(f)
        except:
            print("用户数据库加载失败")
            time.sleep(1)
            continue
        
        # 查找用户
        user_found = False
        for user in users_db["users"]:
            if user["username"] == username:
                user_found = True
                # 修复角色字段检测
                if "role" not in user:
                    user["role"] = "user"
                
                if user["password_hash"] == hash_password(password):
                    current_user = user
                    print(f"登录成功！欢迎 {username}")
                    time.sleep(1)
                    return True
                else:
                    print("密码错误")
                    time.sleep(1)
                    break
        
        if not user_found:
            print("用户名不存在")
            time.sleep(1)

def user_register():
    """用户注册"""
    global current_user
    
    while True:
        clear_screen()
        print("\n======= 用户注册 =======")
        username = input("请输入用户名: ").strip()
        if not username:
            print("用户名不能为空")
            time.sleep(1)
            continue
        
        # 检查用户名是否已存在
        try:
            with open(USERS_FILE, "r") as f:
                users_db = json.load(f)
        except:
            users_db = {"users": []}
        
        username_exists = False
        for user in users_db["users"]:
            if user["username"] == username:
                username_exists = True
                break
                
        if username_exists:
            print("用户名已存在，请选择其他用户名")
            time.sleep(1)
            continue
        else:
            break
    
    # 设置密码
    while True:
        password = input("请输入密码: ").strip()
        confirm = input("请确认密码: ").strip()
        
        if not password:
            print("密码不能为空")
            time.sleep(1)
            continue
            
        if password == confirm:
            break
        print("两次输入的密码不一致")
        time.sleep(1)
    
    # 添加安全信息和邮箱
    print("\n======= 设置安全信息 =======")
    print("（用于找回密码）")
    
    # 设置邮箱
    while True:
        email = input("请输入邮箱: ").strip()
        if not email:
            print("邮箱不能为空")
            continue
        # 简单邮箱格式验证
        if re.match(r"[^@]+@[^@]+\.[^@]+", email):
            break
        print("邮箱格式不正确")
    
    # 设置安全问题
    print("\n请选择安全问题:")
    print("1. 您母亲的姓名是？")
    print("2. 您的出生地是？")
    print("3. 您的第一只宠物的名字是？")
    
    question_choices = {
        "1": "您母亲的姓名是？",
        "2": "您的出生地是？",
        "3": "您的第一只宠物的名字是？"
    }
    
    while True:
        question_choice = input("请选择(1-3): ").strip()
        if question_choice in question_choices:
            security_question = question_choices[question_choice]
            break
        print("无效选择")
    
    security_answer = input("您的答案是: ").strip()
    if not security_answer:
        security_answer = "未设置"
    
    # 创建用户文件夹
    user_folder = f"user_{username}"
    os.makedirs(user_folder, exist_ok=True)
    
    # 创建新用户
    new_user = DEFAULT_USER.copy()
    new_user["username"] = username
    new_user["password_hash"] = hash_password(password)
    new_user["private_folder"] = user_folder
    new_user["created_by"] = current_user["username"] if current_user else "self-register"
    new_user["email"] = email
    new_user["security_question"] = security_question
    new_user["security_answer"] = security_answer
    
    # 添加到数据库
    users_db["users"].append(new_user)
    with open(USERS_FILE, "w") as f:
        json.dump(users_db, f, indent=4)
    
    print(f"用户 {username} 注册成功！")
    time.sleep(1)
    
    # 自动登录
    current_user = new_user
    return True

def recover_password():
    """找回密码 - 修复版"""
    clear_screen()
    print("\n======= 找回密码 =======")
    
    username = input("请输入您的用户名: ").strip()
    if not username:
        print("用户名不能为空")
        time.sleep(1)
        return
    
    # 加载用户数据库
    try:
        with open(USERS_FILE, "r") as f:
            users_db = json.load(f)
    except:
        print("用户数据库加载失败")
        time.sleep(1)
        return
    
    # 查找用户
    user_found = None
    user_index = -1
    for i, user in enumerate(users_db["users"]):
        if user["username"] == username:
            user_found = user
            user_index = i
            break
    
    if not user_found:
        print("用户名不存在")
        time.sleep(1)
        return
    
    # 验证安全问题
    print(f"\n安全问题: {user_found['security_question']}")
    answer = input("您的答案是: ").strip()
    
    if answer != user_found["security_answer"]:
        print("安全答案错误")
        time.sleep(1)
        return
    
    # 设置新密码
    while True:
        new_password = input("请输入新密码: ").strip()
        confirm = input("请确认新极速模式建议关闭密码: ").strip()
        
        if not new_password:
            print("密码不能为空")
            continue
            
        if new_password == confirm:
            # 更新密码
            users_db["users"][user_index]["password_hash"] = hash_password(new_password)
            
            # 保存数据库
            with open(USERS_FILE, "w") as f:
                json.dump(users_db, f, indent=4)
                
            print("\n密码已重置！请使用新密码登录")
            time.sleep(2)
            return
        print("两次输入的密码不一致")
        time.sleep(1)

def init_user_config():
    """初始化当前用户的配置"""
    global config
    
    if not current_user:
        return
    
    # 确保用户有role字段
    if "role" not in current_user:
        current_user["role"] = "user"
    
    # 用户配置文件路径
    config_file = os.path.join(current_user["private_folder"], "hltpz.txt")
    
    # 默认配置（根据用户类型定制）
    DEFAULT_CONFIG = {
        "program_name": f"{current_user['username']}的汉诺塔计时器",
        "time_format": "minutes_seconds",
        "data_file": os.path.join(current_user["private_folder"], "hlt.txt"),
        "data_file_history": [os.path.join(current_user["private_folder"], "hlt.txt")],
        "auto_save": True,
        "show_milliseconds": True,
        "default_top_n": 3,
        "auto_clear": True
    }
    
    # 如果配置文件不存在，创建默认配置
    if not os.path.exists(config_file):
        with open(config_file, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
    
    # 加载配置
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
    except:
        config = DEFAULT_CONFIG.copy()
    
    # 确保包含所有必要的键
    for key in DEFAULT_CONFIG:
        if key not in config:
            config[key] = DEFAULT_CONFIG[key]
    
    # 初始化数据文件
    init_data_file()

def init_data_file():
    """初始化数据文件，如果不存在则创建"""
    data_file = config["data_file"]
    
    if not os.path.exists(data_file):
        try:
            with open(data_file, "w") as f:
                json.dump([], f)
        except Exception as e:
            print(f"创建数据文件失败: {e}")

def load_records():
    """加载历史记录"""
    try:
        data_file = config["data_file"]
        
        with open(data_file, "r") as f:
            return json.load(f)
    except:
        return []

def save_records(records):
    """保存记录到文件"""
    try:
        data_file = config["data_file"]
        
        with open(data_file, "w") as f:
            json.dump(records, f)
    except Exception as e:
        print(f"保存记录失败: {e}")

def format_duration(seconds):
    """根据配置格式化时间显示"""
    if config["time_format"] == "seconds":
        # 纯秒格式
        if config["show_milliseconds"]:
            return f"{seconds:.3f}秒"
        else:
            return f"{int(seconds)}秒"
    else:
        # 分:秒格式
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        
        if config["show_milliseconds"]:
            return f"{minutes}:{remaining_seconds:06.3f}"
        else:
            return f"{minutes}:{int(remaining_seconds):02d}"

def record_time(duration):
    """记录时间并询问用户是否保存"""
    # 显示本次用时
    print(f"\n本次用时: {format_duration(duration)}")
    
    # 如果配置为自动保存，则直接保存
    if config["auto_save"]:
        save_record(duration)
        return
    
    # 否则询问是否保存
    while True:
        response = input("是否保存此次记录？(y/n): ").lower()
        if response == 'y':
            save_record(duration)
            break
        elif response == 'n':
            print("记录未保存")
            break
        else:
            print("无效输入，请输入 'y' 或 'n'")

def save_record(duration):
    """保存记录到文件"""
    # 创建新记录
    new_record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "duration": duration
    }
    
    # 加载所有记录
    records = load_records()
    
    # 添加新记录
    records.append(new_record)
    
    # 保存记录
    save_records(records)
    print("记录已保存！")

def get_top_times(records, n=3):
    """获取最快的n次记录"""
    # 按时间排序
    sorted_records = sorted(records, key=lambda x: x["duration"])
    return sorted_records[:n]

def show_records(records, title="记录列表"):
    """显示记录列表"""
    print(f"\n{title}:")
    if not records:
        print("暂无记录")
        return
    
    for i, record in enumerate(records, 1):
        formatted_time = format_duration(record["duration"])
        print(f"{i}. {formatted_time} - {record['timestamp']}")

def show_top_times():
    """显示最快的前n次记录"""
    records = load_records()
    top_n = config["default_top_n"]
    top_times = get_top_times(records, top_n)
    show_records(top_times, f"最快的前{top_n}次记录")

def show_all_records():
    """显示全部记录"""
    records = load_records()
    # 按时间倒序排列（最新记录在前）
    records.sort(key=lambda x: x["timestamp"], reverse=True)
    show_records(records, "全部记录")

def delete_record():
    """删除特定记录"""
    records = load_records()
    if not records:
        print("没有可删除的记录")
        return
        
    show_all_records()
    try:
        index = int(input("\n请输入要删除的记录序号（0取消）: "))
        if index == 0:
            return
            
        if 1 <= index <= len(records):
            # 确认删除
            confirm = input(f"确认删除记录 #{index}? (y/n): ").lower()
            if confirm == 'y':
                deleted_record = records.pop(index-1)
                save_records(records)
                formatted_time = format_duration(deleted_record["duration"])
                print(f"已删除记录: {formatted_time} - {deleted_record['timestamp']}")
            else:
                print("删除已取消")
        else:
            print("无效的序号")
    except ValueError:
        print("请输入有效的数字")

def add_to_history(path):
    """添加路径到历史记录"""
    # 如果路径已经在历史中，先移除它
    if path in config["data_file_history"]:
        config["data_file_history"].remove(path)
    
    # 添加路径到历史开头
    config["data_file_history"].insert(0, path)
    
    # 限制历史记录长度
    if len(config["data_file_history"]) > MAX_HISTORY:
        config["data_file_history"] = config["data_file_history"][:MAX_HISTORY]
    
    # 保存配置
    save_config()

def save_config():
    """保存当前用户的配置"""
    if not current_user:
        return
        
    config_file = os.path.join(current_user["private_folder"], "hltpz.txt")
    try:
        with open(config_file, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"保存配置失败: {e}")

def select_data_file():
    """选择数据文件路径"""
    if config["auto_clear"]:
        clear_screen()
    
    print(f"\n======= {config['program_name']} - 选择数据文件 =======")
    
    # 显示历史路径
    history = config["data_file_history"]
    print("历史路径:")
    for i, path in enumerate(history, 1):
        exists = os.path.exists(path)
        status = "✓" if exists else "✗✗"
        print(f"{i}. [{status}] {path}")
    
    print("0. 返回")
    print("n. 输入新路径")
    
    # 获取用户选择
    while True:
        choice = input("请选择操作: ")
        
        # 返回
        if choice == "0":
            return None
        
        # 输入新路径
        if choice.lower() == "n":
            new_path = input("请输入新的数据文件路径: ").strip()
            if new_path:
                return new_path
            else:
                print("路径不能为空")
        
        # 选择历史路径
        try:
            index = int(choice)
            if 1 <= index <= len(history):
                return history[index-1]
            else:
                print(f"无效序号，请输入1-{len(history)}的数字")
        except ValueError:
            print("无效输入，请输入数字或'n'")

def rename_data_file():
    """修改当前数据文件的文件名"""
    if config["auto_clear"]:
        clear_screen()
    
    print(f"\n======= {config['program_name']} - 修改数据文件名 =======")
    print(f"当前数据文件: {config["data_file"]}")
    
    # 获取新文件名
    new_name = input("\n请输入新的数据文件名（包括扩展名）: ").strip()
    
    if not new_name:
        print("文件名不能为空")
        return
    
    # 检查是否与当前文件名相同
    if new_name == config["data_file"]:
        print("新文件名与当前文件名相同")
        return
    
    # 记录当前文件路径
    old_path = config["data_file"]
    new_path = new_name
    
    # 检查新文件是否已存在
    if os.path.exists(new_path):
        print(f"文件 '{new_path}' 已存在，无法重命名")
        return
    
    try:
        # 重命名文件
        os.rename(old_path, new_path)
        
        # 更新配置
        config["data_file"] = new_path
        add_to_history(new_path)
        save_config()
        
        print(f"\n数据文件已重命名: {old_path} -> {new_path}")
        print("配置已更新")
        
        # 初始化新数据文件（如果不存在）
        init_data_file()
        
    except Exception as e:
        print(f"重命名失败: {e}")
        print("请检查文件名是否有效")

def import_data():
    """导入数据功能"""
    if config["auto_clear"]:
        clear_screen()
    
    print("\n======= 导入数据 =======")
    print("1. 从文件导入（同目录下的文件）")
    print("2. 输入纯文本内容导入")
    print("0. 返回")
    
    choice = input("请选择导入方式: ")
    
    if choice == "1":
        import_from_file()
    elif choice == "2":
        import_from_text()
    elif choice == "0":
        return
    else:
        print("无效选择")
    input("\n按Enter键返回...")

def import_from_file():
    """从同目录下的文件导入数据"""
    print("\n当前目录下的文件列表:")
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")
    
    try:
        file_num = int(input("请输入要导入的文件序号 (0取消): "))
        if file_num == 0:
            return
            
        if 1 <= file_num <= len(files):
            selected_file = files[file_num-1]
            print(f"准备导入文件: {selected_file}")
            
            try:
                with open(selected_file, 'r') as f:
                    data = json.load(f)
                    
                if validate_data(data):
                    # 加载现有记录
                    existing_records = load_records()
                    
                    # 合并记录
                    existing_records.extend(data)
                    
                    # 保存记录
                    save_records(existing_records)
                    print(f"成功导入 {len(data)} 条记录！")
                else:
                    print("导入失败：数据格式不正确")
            except Exception as e:
                print(f"导入失败: {e}")
        else:
            print("无效的文件序号")
    except ValueError:
        print("请输入有效的数字")

def import_from_text():
    """通过纯文本输入导入数据"""
    print("\n请输入要导入的数据（JSON格式）:")
    print("格式示例: [{'timestamp': '2023-01-01 12:00:00', 'duration': 10.5}, ...]")
    print("输入 'q' 结束输入")
    
    lines = []
    while True:
        line = input()
        if line.lower() == 'q':
            break
        lines.append(line)
    
    text = '\n'.join(lines)
    
    try:
        data = json.loads(text)
        
        if validate_data(data):
            # 加载现有记录
            existing_records = load_records()
            
            # 合并记录
            existing_records.extend(data)
            
            # 保存记录
            save_records(existing_records)
            print(f"成功导入 {len(data)} 条记录！")
        else:
            print("导入失败：数据格式不正确")
    except Exception as e:
        print(f"导入失败: {e}")

def validate_data(data):
    """验证数据格式是否正确"""
    if not isinstance(data, list):
        return False
        
    for item in data:
        if not isinstance(item, dict):
            return False
        if "timestamp" not in item or "duration" not in item:
            return False
        if not isinstance(item["duration"], (int, float)):
            return False
    
    return True

def edit_config():
    """编辑程序配置"""
    global config
    
    while True:
        if config["auto_clear"]:
            clear_screen()
        
        print(f"\n======= {config['program_name']} - 配置管理 =======")
        print(f"1. 程序名称: {config['program_name']}")
        print(f"2. 时间格式: {'分:秒' if config['time_format'] == 'minutes_seconds' else '秒'}")
        print(f"3. 数据文件路径: {config['data_file']}")
        print(f"4. 自动保存记录: {'是' if config['auto_save'] else '否'}")
        print(f"5. 显示毫秒: {'是' if config['show_milliseconds'] else '否'}")
        print(f"6. 默认显示最快记录数: {config['default_top_n']}")
        print(f"7. 自动清屏: {'是' if config['auto_clear'] else '否'}")
        print("8. 修改数据文件名")
        print("9. 导入数据")
        print("0. 返回主菜单")
        
        choice = input("请选择要修改的配置项: ")
        
        if choice == "1":
            new_name = input("请输入新的程序名称: ").strip()
            if new_name:
                config["program_name"] = new_name
                save_config()
                print(f"程序名称已更新为: {new_name}")
            else:
                print("程序名称不能为空")
            
        elif choice == "2":
            new_format = input("选择时间格式 (1=分:秒, 2=秒): ")
            if new_format == "1":
                config["time_format"] = "minutes_seconds"
            elif new_format == "2":
                config["time_format"] = "seconds"
            else:
                print("无效选择，保持原设置")
            save_config()
            
        elif choice == "3":
            # 显示选择菜单
            selected_path = select_data_file()
            
            if selected_path:
                # 更新路径
                config["data_file"] = selected_path
                
                # 添加到历史
                add_to_history(selected_path)
                
                # 保存配置
                save_config()
                print(f"数据文件路径已更新为: {selected_path}")
                
                # 初始化新数据文件
                init_data_file()
            
        elif choice == "4":
            auto_save = input("自动保存记录? (y/n): ").lower()
            if auto_save == "y":
                config["auto_save"] = True
            elif auto_save == "n":
                config["auto_save"] = False
            else:
                print("无效输入，保持原设置")
            save_config()
            
        elif choice == "5":
            show_ms = input("显示毫秒? (y/n): ").lower()
            if show_ms == "y":
                config["show_milliseconds"] = True
            elif show_ms == "n":
                config["show_milliseconds"] = False
            else:
                print("无效输入，保持原设置")
            save_config()
            
        elif choice == "6":
            try:
                new_top_n = int(input("请输入默认显示的最快记录数量: "))
                if new_top_n > 0:
                    config["default_top_n"] = new_top_n
                    save_config()
                else:
                    print("数量必须大于0")
            except ValueError:
                print("请输入有效数字")
                
        elif choice == "7":
            auto_clear = input("自动清屏? (极速模式建议关闭y/n): ").lower()
            if auto_clear == "y":
                config["auto_clear"] = True
            elif auto_clear == "n":
                config["auto极速模式建议关闭_clear"] = False
            else:
                print("无效输入，保持原设置")
            save_config()
            
        elif choice == "8":
            rename_data_file()
            input("\n按Enter键返回配置菜单...")
            
        elif choice == "9":
            import_data()
            input("\n按Enter键返回配置菜单...")
            
        elif choice == "0":
            break
            
        else:
            print("无效选择，请重新输入")

def main_timer():
    """计时器主函数"""
    while True:  # 添加外层循环以支持重新开始
        if config["auto_clear"]:
            clear_screen()
        
        print(f"\n准备开始{config['program_name']}...")
        input("按Enter键开始计时，完成后再次按")
def import_from_text():
    """通过纯文本输入导入数据"""
    print("\n请输入要导入的数据（JSON格式）:")
    print("格式示例: [{'timestamp': '2023-01-01 12:00:00', 'duration': 10.5}, ...]")
    print("输入 'q' 结束输入")
    
    lines = []
    while True:
        line = input()
        if line.lower() == 'q':
            break
        lines.append(line)
    
    text = '\n'.join(lines)
    
    try:
        data = json.loads(text)
        
        if validate_data(data):
            # 加载现有记录
            existing_records = load_records()
            
            # 合并记录
            existing_records.extend(data)
            
            # 保存记录
            save_records(existing_records)
            print(f"成功导入 {len(data)} 条记录！")
        else:
            print("导入失败：数据格式不正确")
    except Exception as e:
        print(f"导入失败: {e}")

def validate_data(data):
    """验证数据格式是否正确"""
    if not isinstance(data, list):
        return False
        
    for item in data:
        if not isinstance(item, dict):
            return False
        if "timestamp" not in item or "duration" not in item:
            return False
        if not isinstance(item["duration"], (int, float)):
            return False
    
    return True

def edit_config():
    """编辑程序配置"""
    global config
    
    while True:
        if config["auto_clear"]:
            clear_screen()
        
        print(f"\n======= {config['program_name']} - 配置管理 =======")
        print(f"1. 程序名称: {config['program_name']}")
        print(f"2. 时间格式: {'分:秒' if config['time_format'] == 'minutes_seconds' else '秒'}")
        print(f"3. 数据文件路径: {config['data_file']}")
        print(f"4. 自动保存记录: {'是' if config['auto_save'] else '否'}")
        print(f"5. 显示毫秒: {'是' if config['show_milliseconds'] else '否'}")
        print(f"6. 默认显示最快记录数: {config['default_top_n']}")
        print(f"7. 自动清屏: {'是' if config['auto_clear'] else '否'}")
        print("8. 修改数据文件名")
        print("9. 导入数据")
        print("0. 返回主菜单")
        
        choice = input("请选择要修改的配置项: ")
        
        if choice == "1":
            new_name = input("请输入新的程序名称: ").strip()
            if new极速模式建议关闭_name:
                config["program_name"] = new_name
                save_config()
                print(f"程序名称已更新为: {new_name}")
            else:
                print("程序名称不能为空")
            
        elif choice == "2":
            new_format = input("选择时间格式 (1=分:秒, 2=秒): ")
            if new_format == "1":
                config["time_format"] = "minutes_seconds"
            elif new_format == "2":
                config["time_format"] = "seconds"
            else:
                print("无效选择，保持原设置")
            save_config()
            
        elif choice == "3":
            # 显示选择菜单
            selected_path = select_data_file()
            
            if selected_path:
                # 更新路径
                config["data_file"] = selected_path
                
                # 添加到历史
                add_to_history(selected_path)
                
                # 保存配置
                save_config()
                print(f"数据文件路径已更新为: {selected_path}")
                
                # 初始化新数据文件
                init_data_file()
            
        elif choice == "4":
            auto_save = input("自动保存记录? (y/n): ").lower()
            if auto_save == "y":
                config["auto_save"] = True
            elif auto_save == "n":
                config["auto_save"] = False
            else:
                print("无效输入，保持原设置")
            save_config()
            
        elif choice == "5":
            show_ms = input("显示毫秒? (y/n): ").lower()
            if show_ms == "y":
                config["show_milliseconds"] = True
            elif show_ms == "n":
                config["show_milliseconds"] = False
            else:
                print("无效输入，保持原设置")
            save_config()
            
        elif choice == "6":
            try:
                new_top_n = int(input("请输入默认显示的最快记录数量: "))
                if new_top_n > 0:
                    config["default_top_n"] = new_top_n
                    save_config()
                else:
                    print("数量必须大于0")
            except ValueError:
                print("请输入有效数字")
                
        elif choice == "7":
            auto_clear = input("自动清屏? (y/n): ").lower()
            if auto_clear == "y":
                config["auto_clear"] = True
            elif auto_clear == "n":
                config["auto_clear"] = False
            else:
                print("无效输入，保持原设置")
            save_config()
            
        elif choice == "8":
            rename_data_file()
            input("\n按Enter键返回配置菜单...")
            
        elif choice == "9":
            import_data()
            input("\n按Enter键返回配置菜单...")
            
        elif choice == "0":
            break
            
        else:
            print("无效选择，请重新输入")

def main_timer():
    """计时器主函数"""
    while True:  # 添加外层循环以支持重新开始
        if config["auto_clear"]:
            clear_screen()
        
        print(f"\n准备开始{config['program_name']}...")
        input("按Enter键开始计时，完成后再次按Enter结束计时...")
        
        if config["auto_clear"]:
            clear_screen()
        
        # 第一次按键 - 开始计时
        start_time = time.perf_counter()
        
        print(f"{config['program_name']}开始！")
        input("完成后按Enter结束...")
        
        # 第二次按键 - 结束计时
        end_time = time.perf_counter()
        
        # 计算用时
        duration = end_time - start_time
        
        # 记录本次时间
        record_time(duration)
        
        # 添加重新开始选项
        while True:
            choice = input("\n请选择操作: (1)重新计时 (2)返回主菜单: ")
            if choice == "1":
                print("准备重新开始计时...")
                time.sleep(0.5)  # 短暂延迟让用户看到提示
                break  # 跳出内层循环，重新开始计时
            elif choice == "2":
                return  # 返回主菜单
            else:
                print("无效选择，请重新输入")

def admin_menu():
    """管理员菜单"""
    while True:
        clear_screen()
        print("\n======= 管理员菜单 =======")
        print("1. 查看所有用户")
        print("2. 删除用户")
        print("3. 重置用户密码")
        print("4. 创建新账号")
        print("5. 设置子管理员")
        print("6. 返回主菜单")
        
        choice = input("请选择操作: ")
        
        if choice == "1":
            list_users()
        elif choice == "2":
            delete_user()
        elif choice == "3":
            reset_user_password()
        elif choice == "4":
            create_user()
        elif choice == "5":
            set_subadmin()
        elif choice == "6":
            break
        else:
            print("无效选择")

def list_users():
    """列出所有用户"""
    try:
        with open(USERS_FILE, "r") as f:
            users_db = json.load(f)
    except:
        print("无法加载用户数据库")
        return
    
    print("\n用户列表:")
    print("{:<15} {:<10} {:<15} {:<15}".format("用户名", "角色", "创建者", "文件夹"))
    print("-" * 55)
    
    for user in users_db["users"]:
        # 确保角色字段存在
        role = "管理员" if user.get("role", "user") == "admin" else "子管理员" if user.get("role", "user") == "subadmin" else "用户"
        print("{:<15} {:<10} {:<15} {:<15}".format(
            user["username"], 
            role,
            user.get("created_by", "未知"),
            user["private_folder"]
        ))
    
    input("\n按Enter键返回...")

def delete_user():
    """删除用户"""
    username = input("请输入要删除的用户名: ").strip()
    
    if username == ADMIN_USERNAME:
        print("不能删除主管理员账户")
        return
    
    try:
        with open(USERS_FILE, "r") as f:
            users_db = json.load(f)
    except:
        print("无法加载用户数据库")
        return
    
    # 查找并删除用户
    found = False
    for i, user in enumerate(users_db["users"]):
        if user["username"] == username:
            found = True
            
            # 确保角色字段存在
            user_role = user.get("role", "user")
            
            # 检查权限：管理员可以删除所有用户，子管理员只能删除普通用户
            if current_user.get("role", "user") == "subadmin" and user_role != "user":
                print("子管理员只能删除普通用户")
                break
            else:
                # 删除用户文件夹
                user_folder = user["private_folder"]
                if os.path.exists(user_folder):
                    try:
                        shutil.rmtree(user_folder)
                        print(f"已删除用户文件夹: {user_folder}")
                    except Exception as e:
                        print(f"删除文件夹失败: {e}")
                
                # 从数据库中删除
                del users_db["users"][i]
                
                # 保存数据库
                with open(USERS_FILE, "w") as f:
                    json.dump(users_db, f, indent=4)
                
                print(f"用户 {username} 已删除")
                break
    
    if not found:
        print("用户不存在")
    
    input("\n按Enter键返回...")

def reset_user_password():
    """重置用户密码"""
    username = input("请输入要重置密码的用户名: ").strip()
    if not username:
        print("用户名不能为空")
        return
    
    try:
        with open(USERS_FILE, "r") as f:
            users_db = json.load(f)
    except:
        print("无法加载用户数据库")
        return
    
    user_found = False
    for user in users_db["users"]:
        if user["username"] == username:
            user_found = True
            # 生成随机密码
            new_password = "123456"  # 简单起见，使用固定密码
            
            # 更新密码
            user["password_hash"] = hash_password(new_password)
            
            # 保存数据库

            with open(USERS_FILE, "w") as f:
                json.dump(users_db, f, indent=4)
                
            print(f"用户 {username} 的密码已重置为: {new_password}")
            print("请通知用户尽快修改密码")
            break
    
    if not user_found:
        print("用户不存在")
    
    input("\n按Enter键返回...")

def create_user():
    """管理员创建新账号"""
    clear_screen()
    print("\n======= 创建新用户 =======")
    
    username = input("请输入用户名: ").strip()
    if not username:
        print("用户名不能为空")
        return
    
    # 检查用户名是否已存在
    try:
        with open(USERS_FILE, "r") as f:
            users_db = json.load(f)
    except:
        users_db = {"users": []}
    
    for user in users_db["users"]:
        if user["username"] == username:
            print("用户名已存在")
            return
    
    # 设置密码
    password = input("请输入初始密码: ").strip()
    if not password:
        print("密码不能为空")
        return
    
    # 设置角色
    print("选择用户角色:")
    print("1. 普通用户")
    print("2. 子管理员")
    role_choice = input("请选择(1-2): ").strip()
    if role_choice == "1":
        role = "user"
    elif role_choice == "2":
        role = "subadmin"
    else:
        print("无效选择，默认为普通用户")
        role = "user"
    
    # 创建用户文件夹
    user_folder = f"user_{username}"
    os.makedirs(user_folder, exist_ok=True)
    
    # 创建新用户
    new_user = DEFAULT_USER.copy()
    new_user["username"] = username
    new_user["password_hash"] = hash_password(password)
    new_user["private_folder"] = user_folder
    new_user["created_by"] = current_user["username"]
    new_user["role"] = role
    
    # 添加到数据库
    users_db["users"].append(new_user)
    with open(USERS_FILE, "w") as f:
        json.dump(users_db, f, indent=4)
    
    print(f"用户 {username} 创建成功！")
    input("\n按Enter键返回...")

def set_subadmin():
    """设置子管理员"""
    username = input("请输入要设置为子管理员的用户名: ").strip()
    if not username:
        print("用户名不能为空")
        return
    
    try:
        with open(USERS_FILE, "r") as f:
            users_db = json.load(f)
    except:
        print("无法加载用户数据库")
        return
    
    user_found = False
    for user in users_db["users"]:
        if user["username"] == username:
            user_found = True
            user["role"] = "subadmin"
            
            # 保存数据库
            with open(USERS_FILE, "w") as f:
                json.dump(users_db, f, indent=4)
                
            print(f"用户 {username} 已设置为子管理员")
            break
    
    if not user_found:
        print("用户不存在")
    
    input("\n按Enter键返回...")

def main_menu():
    """主菜单（带用户系统）"""
    global current_user
    
    # 初始化用户系统
    init_user_system()
    
    while True:
        clear_screen()
        print("\n======= 汉诺塔计时器 - 多用户版 =======")
        
        if current_user:
            print(f"当前用户: {current_user['username']} ({'管理员' if current_user.get('role') == 'admin' else '子管理员' if current_user.get('role') == 'subadmin' else '普通用户'})")
            print("\n1. 开始计时")
            print("2. 查看最快记录")
            print("3. 查看所有记录")
            print("4. 删除记录")
            print("5. 程序配置")
            
            if current_user.get("role") in ["admin", "subadmin"]:
                print("6. 管理员菜单")
            
            print("7. 注销")
            print("8. 退出程序")
        else:
            print("\n1. 登录")
            print("2. 注册")
            print("3. 找回密码")
            print("4. 退出程序")
        
        choice = input("\n请选择操作: ")
        
        if current_user:
            if choice == "1":
                # 初始化用户配置
                init_user_config()
                main_timer()
            elif choice == "2":
                init_user_config()
                show_top_times()
                input("\n按Enter键返回主菜单...")
            elif choice == "3":
                init_user_config()
                show_all_records()
                input("\n按Enter键返回主菜单...")
            elif choice == "4":
                init_user_config()
                delete_record()
                input("\n按Enter键返回主菜单...")
            elif choice == "5":
                init_user_config()
                edit_config()
            elif choice == "6" and current_user.get("role") in ["admin", "subadmin"]:
                init_user_config()
                admin_menu()
            elif choice == "7":
                current_user = None
                print("已注销")
                time.sleep(1)
            elif choice == "8":
                print("感谢使用，再见！")
                break
            else:
                print("无效选择")
                time.sleep(1)
        else:
            if choice == "1":
                if user_login():
                    init_user_config()
            elif choice == "2":
                user_register()
            elif choice == "3":
                recover_password()
            elif choice == "4":
                print("感谢使用，再见！")
                break
            else:
                print("无效选择")
                time.sleep(1)

# 程序入口
if __name__ == "__main__":
    main_menu()

