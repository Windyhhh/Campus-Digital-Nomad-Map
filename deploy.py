#!/usr/bin/env python3
"""
校园数字游民活地图 - 一键部署脚本
Campus Digital Nomad Live Map - One-Click Deployment Script

功能：
1. 检查Python环境
2. 创建虚拟环境（可选）
3. 安装依赖包
4. 初始化数据库
5. 启动应用

使用方法：
    python deploy.py              # 完整部署
    python deploy.py --skip-venv  # 跳过虚拟环境创建
    python deploy.py --dev        # 开发模式（启用调试）
    python deploy.py --prod       # 生产模式（使用gunicorn）
"""

import os
import sys
import subprocess
import platform
import argparse
import time
from pathlib import Path

# 颜色输出
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """打印标题"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    """打印成功信息"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_info(text):
    """打印信息"""
    print(f"{Colors.OKBLUE}ℹ {text}{Colors.ENDC}")

def print_warning(text):
    """打印警告"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_error(text):
    """打印错误"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def run_command(command, description, check=True):
    """运行命令并显示结果"""
    print_info(f"{description}...")
    try:
        if isinstance(command, str):
            result = subprocess.run(command, shell=True, check=check, 
                                  capture_output=True, text=True)
        else:
            result = subprocess.run(command, check=check, 
                                  capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success(f"{description} 完成")
            return True
        else:
            if result.stderr:
                print_error(f"{description} 失败: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        print_error(f"{description} 失败: {e}")
        return False
    except Exception as e:
        print_error(f"{description} 出错: {e}")
        return False

def check_python_version():
    """检查Python版本"""
    print_header("检查Python环境")
    
    version = sys.version_info
    print_info(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print_error("需要Python 3.7或更高版本")
        return False
    
    print_success("Python版本符合要求")
    return True

def create_virtual_environment(skip_venv=False):
    """创建虚拟环境"""
    if skip_venv:
        print_warning("跳过虚拟环境创建")
        return True
    
    print_header("创建虚拟环境")
    
    venv_path = Path("venv")
    if venv_path.exists():
        print_warning("虚拟环境已存在，跳过创建")
        return True
    
    return run_command([sys.executable, "-m", "venv", "venv"], 
                      "创建虚拟环境")

def get_pip_command():
    """获取pip命令"""
    system = platform.system()
    if system == "Windows":
        if Path("venv/Scripts/pip.exe").exists():
            return "venv\\Scripts\\pip.exe"
        return "pip"
    else:
        if Path("venv/bin/pip").exists():
            return "venv/bin/pip"
        return "pip3"

def get_python_command():
    """获取python命令"""
    system = platform.system()
    if system == "Windows":
        if Path("venv/Scripts/python.exe").exists():
            return "venv\\Scripts\\python.exe"
        return "python"
    else:
        if Path("venv/bin/python").exists():
            return "venv/bin/python"
        return "python3"

def install_dependencies():
    """安装依赖包"""
    print_header("安装依赖包")
    
    if not Path("requirements.txt").exists():
        print_error("requirements.txt 文件不存在")
        return False
    
    pip_cmd = get_pip_command()
    
    # 升级pip
    run_command(f"{pip_cmd} install --upgrade pip", "升级pip", check=False)
    
    # 安装依赖
    return run_command(f"{pip_cmd} install -r requirements.txt", 
                      "安装项目依赖")

def create_env_file():
    """创建.env文件"""
    print_header("配置环境变量")
    
    env_path = Path(".env")
    if env_path.exists():
        print_warning(".env 文件已存在，跳过创建")
        return True
    
    env_content = """# 数据库配置
DATABASE_URL=sqlite:///campus_map.db

# Flask密钥（生产环境请修改为随机字符串）
SECRET_KEY=dev-secret-key-please-change-in-production

# Flask环境
FLASK_ENV=development
FLASK_DEBUG=True

# 应用配置
APP_NAME=校园数字游民活地图
APP_HOST=127.0.0.1
APP_PORT=5000
"""
    
    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print_success("创建 .env 文件")
        return True
    except Exception as e:
        print_error(f"创建 .env 文件失败: {e}")
        return False

def initialize_database():
    """初始化数据库"""
    print_header("初始化数据库")
    
    if not Path("init_db.py").exists():
        print_error("init_db.py 文件不存在")
        return False
    
    python_cmd = get_python_command()
    return run_command(f"{python_cmd} init_db.py", "初始化数据库")

def start_application(mode='dev'):
    """启动应用"""
    print_header("启动应用")
    
    python_cmd = get_python_command()
    
    if mode == 'prod':
        print_info("生产模式启动（使用gunicorn）")
        print_warning("请确保已安装gunicorn: pip install gunicorn")
        cmd = "gunicorn -w 4 -b 0.0.0.0:5000 app:app"
    else:
        print_info("开发模式启动")
        cmd = f"{python_cmd} app.py"
    
    print_success("应用启动命令准备完成")
    print_info(f"启动命令: {cmd}")
    print_info("按 Ctrl+C 停止应用")
    print("")
    print(f"{Colors.OKGREEN}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.OKGREEN}{Colors.BOLD}应用已启动！{Colors.ENDC}")
    print(f"{Colors.OKGREEN}访问地址: http://127.0.0.1:5000{Colors.ENDC}")
    print(f"{Colors.OKGREEN}示例账户: admin / admin123{Colors.ENDC}")
    print(f"{Colors.OKGREEN}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
    
    try:
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print_info("\n应用已停止")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='校园数字游民活地图 - 一键部署脚本')
    parser.add_argument('--skip-venv', action='store_true', 
                       help='跳过虚拟环境创建')
    parser.add_argument('--dev', action='store_true', 
                       help='开发模式（默认）')
    parser.add_argument('--prod', action='store_true', 
                       help='生产模式（使用gunicorn）')
    parser.add_argument('--no-start', action='store_true', 
                       help='只部署不启动')
    
    args = parser.parse_args()
    
    # 确定运行模式
    mode = 'prod' if args.prod else 'dev'
    
    print(f"{Colors.OKCYAN}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                                                            ║")
    print("║          校园数字游民活地图 - 一键部署脚本                ║")
    print("║     Campus Digital Nomad Live Map - Deployment Script     ║")
    print("║                                                            ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")
    
    # 执行部署步骤
    steps = [
        ("检查Python环境", lambda: check_python_version()),
        ("创建虚拟环境", lambda: create_virtual_environment(args.skip_venv)),
        ("安装依赖包", lambda: install_dependencies()),
        ("配置环境变量", lambda: create_env_file()),
        ("初始化数据库", lambda: initialize_database()),
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print_error(f"\n部署失败：{step_name} 步骤出错")
            sys.exit(1)
        time.sleep(0.5)  # 短暂延迟，让输出更清晰
    
    print_header("部署完成")
    print_success("所有部署步骤已成功完成！")
    
    if not args.no_start:
        print_info("准备启动应用...")
        time.sleep(2)
        start_application(mode)
    else:
        print_info("跳过应用启动")
        print_info(f"手动启动命令: {get_python_command()} app.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_info("\n\n部署已取消")
        sys.exit(0)
    except Exception as e:
        print_error(f"\n部署过程中出现错误: {e}")
        sys.exit(1)
