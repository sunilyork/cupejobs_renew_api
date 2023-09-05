# README

This README would normally document whatever steps are necessary to get your application up and running.

### What is this repository for?

- Quick summary
- Version
- [Learn Markdown](https://bitbucket.org/tutorials/markdowndemo)

### How do I get set up?

- Summary of set up
- Configuration
- Dependencies
- Database configuration
- How to run tests
- Deployment instructions

1.  **Virtual Environment / Dependencies set up**

    - cd cupejobs-renew_api/
    - python3 -m venv --prompt cupejobs_api .venv
    - source .venv/bin/activate
    - python3 -m pip install --upgrade pip
    - python3 -m pip install pip-tools
    - python3 -m piptools compile or pip-compile
    - pip install -r requirements.txt


2. **Update config/init.py**: Replace placeholder 'PATH_TO_FILE' with the  location of the .env file


3. **Environment Variables**
     - DB_NAME=
     - DB_URL="mongodb://${USERNAME}:${PASSWORD}@127.0.0.1:27017/${DB_NAME}?authSource=admin&compressors=zlib&readPreference=primary&appname=MongoDB%20Compass&ssl=false"
     - ARMS_API_URL=http://localhost:8002
     - CUPEJOBS_UI_URL=http://localhost:3000
     - JWT_SECRET_KEY=/PATH_TO_/jwt_secret_key.txt
     - JWT_SECRET_KEY_ID_RSA_PASSWORD=
     - JWT_ACCESS_TOKEN_SECRET_KEY_PRIVATE_KEY=/PATH_TO_/private.pem
     - JWT_ACCESS_TOKEN_SECRET_KEY_PUBLIC_KEY=/PATH_TO_/public.pem
     - JWT_REFRESH_TOKEN_SECRET_KEY_PRIVATE_KEY=/PATH_TO_/private.pem
     - JWT_REFRESH_TOKEN_SECRET_KEY_PUBLIC_KEY=/PATH_TO_/public.pem


4. **JWT, Encryption, RSA Key Pair**
   - How to Handle JWTs in Python: https://auth0.com/blog/how-to-handle-jwt-in-python/
   - Encrypt SSID and PAYNO: https://milovantomasevic.com/blog/stackoverflow/2021-04-28-how-do-i-encrypt-and-decrypt-a-string-in-python
   - Generate OpenSSL RSA Key Pair from the Command Line https://rietta.com/blog/openssl-generating-rsa-key-from-command/