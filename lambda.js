const AWS = require('aws-sdk');

const ddb = new AWS.DynamoDB.DocumentClient({convertEmptyValues: true});

exports.handler = (event, context, callback) => {
    console.log(event)
    const method = event['http-method']
    
    if(method == 'GET'){
        console.log('GET')
        getAllData(callback)
        
    }else if(method == 'POST'){
        console.log('POST')
        const body = event['body']
        putData(body.data)
    }
};

let getAllData = (callback) => {
    let params = {
        TableName : "wuhan"
    };

    const results = ddb.scan(params).promise()
    
    let response = results.then((data)=>{
        console.log(data)
        callback(null, {
            'data':data['Items']
        });
    }).catch((err)=>{
        console.log(err)
    })
    return response
}

let putData = (data) => {
    data.forEach((d)=>{
        var params = {
            TableName: "wuhan",
            Item: {
                "id": d.id,
                "city":  d.city,
                "country": d.country,
                "long":  d.long,
                "lat":  d.lat,
                "update_time": d.update_time,
                "confirm":  parseInt(d.confirm),
                "death":  parseInt(d.death),
                "recover":  parseInt(d.recover),
            }
        };
        
        console.log(d)
    
        ddb.put(params, function(err, data) {
            console.log('put')
            if (err) {
               console.error("Error JSON:", JSON.stringify(err, null, 2));
            } else {
               console.log("PutItem succeeded:", data.city);
            }
        });
    });
}
