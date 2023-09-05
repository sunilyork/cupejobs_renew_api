db.getSiblingDB('admin').auth(process.env.MONGO_INITDB_ROOT_USERNAME,process.env.MONGO_INITDB_ROOT_PASSWORD)

db = db.getSiblingDB('admin')

db.createUser({
    user: process.env.MONGO_APP_USERNAME,
    pwd: process.env.MONGO_APP_PASSWORD,
    roles: [
        {
          role: 'readWrite',
          db: process.env.MONGO_INITDB_DATABASE,
        },
    ]
});
