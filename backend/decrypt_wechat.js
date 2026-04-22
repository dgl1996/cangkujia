/**
 * 微信支付回调解密脚本
 * 使用Node.js crypto.createDecipheriv进行AES-256-GCM解密
 * 
 * 原因：Python的cryptography库AESGCM与微信GCM密文格式不兼容
 * 解决方案：通过Node.js子进程调用此脚本进行解密
 * 
 * 使用方法：node decrypt_wechat.js <apiV3Key> <associatedData> <nonce> <ciphertext>
 */

const crypto = require('crypto');

// 从命令行参数获取参数
const apiV3Key = process.argv[2];
const associatedData = process.argv[3];
const nonce = process.argv[4];
const ciphertext = process.argv[5];

function decryptWechatCallback() {
  try {
    // 将APIv3密钥转换为Buffer（utf8编码）
    const key = Buffer.from(apiV3Key, 'utf8');
    
    // 解码ciphertext（base64）
    const ciphertextBuffer = Buffer.from(ciphertext, 'base64');
    
    // nonce使用utf8编码
    const nonceBuffer = Buffer.from(nonce, 'utf8');
    
    // associated_data使用utf8编码
    const associatedDataBuffer = Buffer.from(associatedData, 'utf8');
    
    // 分离密文和认证标签（最后16字节）
    const data = ciphertextBuffer.subarray(0, ciphertextBuffer.length - 16);
    const tag = ciphertextBuffer.subarray(ciphertextBuffer.length - 16);
    
    // 创建 decipher
    const decipher = crypto.createDecipheriv('aes-256-gcm', key, nonceBuffer);
    
    // 设置认证标签
    decipher.setAuthTag(tag);
    
    // 设置附加数据
    decipher.setAAD(associatedDataBuffer);
    
    // 解密
    let decrypted = decipher.update(data, null, 'utf8');
    decrypted += decipher.final('utf8');
    
    // 输出解密结果
    console.log(decrypted);
    process.exit(0);
  } catch (error) {
    console.error('解密失败:', error.message);
    process.exit(1);
  }
}

// 执行解密
decryptWechatCallback();
