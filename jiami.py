import rsa
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64
import os

class HybridEncryption:
    """
    混合加密实现 (使用 rsa 和 pycryptodome)
    思路：用 AES (对称) 加密数据，用 RSA (非对称) 加密 AES 密钥
    """

    @staticmethod
    def generate_rsa_keys(key_size=2048):
        """生成 RSA 密钥对"""
        (public_key, private_key) = rsa.newkeys(key_size)
        return private_key, public_key

    @staticmethod
    def save_keys(private_key, public_key, priv_path='private.pem', pub_path='public.pem'):
        """保存密钥到文件"""
        with open(priv_path, 'wb') as f:
            f.write(private_key.save_pkcs1('PEM'))
        with open(pub_path, 'wb') as f:
            f.write(public_key.save_pkcs1('PEM'))
        print(f"[+] 私钥已保存: {priv_path}")
        print(f"[+] 公钥已保存: {pub_path}")

    @staticmethod
    def load_private_key(key_path='private.pem'):
        """从文件加载私钥"""
        with open(key_path, 'rb') as f:
            key_data = f.read()
        return rsa.PrivateKey.load_pkcs1(key_data)

    @staticmethod
    def load_public_key(key_path='public.pem'):
        """从文件加载公钥"""
        with open(key_path, 'rb') as f:
            key_data = f.read()
        return rsa.PublicKey.load_pkcs1(key_data)

    @staticmethod
    def encrypt_data(data, public_key):
        """
        加密数据
        步骤：1. 生成随机AES密钥 2. 用AES加密数据 3. 用RSA加密AES密钥
        """
        if isinstance(data, str):
            data = data.encode('utf-8')

        # 1. 生成随机 AES 密钥 (32字节 = 256位) 和初始向量 IV
        aes_key = get_random_bytes(32)
        iv = get_random_bytes(16)  # AES 块大小为 16 字节

        # 2. 使用 AES-CBC 模式加密数据
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        # 先对数据进行填充，使其长度为块大小的整数倍
        padded_data = pad(data, AES.block_size)
        encrypted_data = cipher.encrypt(padded_data)

        # 3. 使用 RSA 公钥加密 AES 密钥
        # 注意：RSA 加密有长度限制，这里直接加密 32 字节的 AES 密钥
        encrypted_aes_key = rsa.encrypt(aes_key, public_key)

        # 返回 Base64 编码的结果，方便传输和存储
        return {
            'encrypted_aes_key': base64.b64encode(encrypted_aes_key).decode('utf-8'),
            'iv': base64.b64encode(iv).decode('utf-8'),
            'encrypted_data': base64.b64encode(encrypted_data).decode('utf-8')
        }

    @staticmethod
    def decrypt_data(encrypted_package, private_key):
        """解密数据"""
        # 解码 Base64 数据
        encrypted_aes_key = base64.b64decode(encrypted_package['encrypted_aes_key'])
        iv = base64.b64decode(encrypted_package['iv'])
        encrypted_data = base64.b64decode(encrypted_package['encrypted_data'])

        # 1. 用 RSA 私钥解密出 AES 密钥
        aes_key = rsa.decrypt(encrypted_aes_key, private_key)

        # 2. 用 AES 密钥解密数据
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        decrypted_padded = cipher.decrypt(encrypted_data)
        # 去除填充
        original_data = unpad(decrypted_padded, AES.block_size)

        return original_data.decode('utf-8')

    @staticmethod
    def encrypt_file(file_path, public_key, output_path=None):
        """加密文件"""
        if not output_path:
            output_path = file_path + '.enc'

        with open(file_path, 'rb') as f:
            file_data = f.read()

        encrypted_package = HybridEncryption.encrypt_data(file_data, public_key)

        # 将加密包写入文件
        with open(output_path, 'w') as f:
            f.write(encrypted_package['encrypted_aes_key'] + '\n')
            f.write(encrypted_package['iv'] + '\n')
            f.write(encrypted_package['encrypted_data'])

        print(f"[+] 文件加密完成: {output_path}")
        return output_path

    @staticmethod
    def decrypt_file(encrypted_file_path, private_key, output_path=None):
        """解密文件"""
        if not output_path:
            output_path = encrypted_file_path.replace('.enc', '.dec')

        with open(encrypted_file_path, 'r') as f:
            lines = f.readlines()
            encrypted_package = {
                'encrypted_aes_key': lines[0].strip(),
                'iv': lines[1].strip(),
                'encrypted_data': lines[2].strip()
            }

        decrypted_data = HybridEncryption.decrypt_data(encrypted_package, private_key)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(decrypted_data)

        print(f"[+] 文件解密完成: {output_path}")
        return output_path


def main_demo():
    """演示完整功能"""
    print("=" * 50)
    print("混合加密演示 (使用 rsa + pycryptodome)")
    print("=" * 50)

    # 1. 生成密钥对
    print("\n[1] 正在生成 RSA-2048 密钥对...")
    priv_key, pub_key = HybridEncryption.generate_rsa_keys(2048)
    HybridEncryption.save_keys(priv_key, pub_key)

    # 2. 加密一段文本
    print("\n[2] 正在加密文本...")
    secret_message = "这是一条绝密信息，来自Termux！"
    print(f"   原始文本: {secret_message}")

    encrypted = HybridEncryption.encrypt_data(secret_message, pub_key)
    print(f"   加密后的 AES 密钥 (Base64): {encrypted['encrypted_aes_key'][:50]}...")
    print(f"   加密后的数据 (Base64): {encrypted['encrypted_data'][:50]}...")

    # 3. 解密文本
    print("\n[3] 正在解密文本...")
    decrypted = HybridEncryption.decrypt_data(encrypted, priv_key)
    print(f"   解密结果: {decrypted}")

    # 4. 验证
    print("\n[4] 验证结果...")
    if secret_message == decrypted:
        print("   ✅ 加密解密成功！文本一致。")
    else:
        print("   ❌ 解密失败！")

    # 5. 文件加密演示
    print("\n" + "=" * 50)
    print("文件加密演示")
    print("=" * 50)

    # 创建测试文件
    test_content = """这是一个测试文件。
包含多行内容。
第二行。
第三行，带有特殊符号：!@#$%^&*()。
最后一行。"""
    test_file = "test_document.txt"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    print(f"[+] 创建测试文件: {test_file}")

    # 加密文件
    enc_file = HybridEncryption.encrypt_file(test_file, pub_key)

    # 解密文件
    dec_file = HybridEncryption.decrypt_file(enc_file, priv_key)

    # 验证文件内容
    with open(dec_file, 'r', encoding='utf-8') as f:
        restored_content = f.read()
    if test_content == restored_content:
        print("   ✅ 文件加密解密成功！")
    else:
        print("   ❌ 文件解密后内容不一致！")

    # 清理
    import os
    for f in [test_file, enc_file, dec_file]:
        if os.path.exists(f):
            os.remove(f)
            print(f"[+] 已清理: {f}")

    print("\n" + "=" * 50)
    print("演示完成！您可以使用 HybridEncryption 类进行加密解密。")
    print("=" * 50)


if __name__ == '__main__':
    # 直接运行演示
    main_demo()

    # 您也可以像下面这样在您自己的代码中使用：
    """
    # 初始化
    enc_tool = HybridEncryption

    # 生成并保存密钥
    priv, pub = enc_tool.generate_rsa_keys()
    enc_tool.save_keys(priv, pub)

    # 加密
    my_secret = "我的密码是123456"
    encrypted_pkg = enc_tool.encrypt_data(my_secret, pub)

    # 解密
    decrypted_msg = enc_tool.decrypt_data(encrypted_pkg, priv)
    print(decrypted_msg)  # 输出: 我的密码是123456
    """

