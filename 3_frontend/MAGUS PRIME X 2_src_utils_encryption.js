```javascript
  const crypto = require('crypto');
  const { v4: uuidv4 } = require('uuid');

  const ENCRYPTION_KEY = 'your-secret-key-32-bytes'; // Replace with a secure key

  function encrypt(text) {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv('aes-256-cbc', ENCRYPTION_KEY, iv);
    let encrypted = cipher.update(text);
    encrypted = Buffer.concat([encrypted, cipher.final()]);
    return {
      iv: iv.toString('hex'),
      encryptedData: encrypted.toString('hex'),
    };
  }

  function decrypt(encryptedData, iv) {
    const decipher = crypto.createDecipheriv('aes-256-cbc', ENCRYPTION_KEY, Buffer.from(iv, 'hex'));
    let decrypted = decipher.update(Buffer.from(encryptedData, 'hex'));
    decrypted = Buffer.concat([decrypted, decipher.final()]);
    return decrypted.toString('utf8');
  }

  module.exports = {
    encrypt,
    decrypt,
  };
  ```;
