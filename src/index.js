import http from 'http'; // enable us create our server
import express from 'express';
import bodyParser from 'body-parser';
import mongoose from 'mongoose';
import passport from 'passport';
import cors from 'cors';
// const LocalStrategy = require('passport-local').Strategy; // Depending on the authentication used, could be facebook strategy gmail etc

import config from './config';
import routes from './routes';
import dbConfig from './config/db.config';

const ngrok = require('ngrok');



let app = express();
app.server = http.createServer(app);


// middleware
// parse application/json
app.use(bodyParser.json({
  limit: config.bodyLimit
}));

// passport Config
// app.use(passport.initialize());
// let Account = require('./model/account');
// passport.use(new LocalStrategy({
//   usernameField: 'email',
//   passwordField: 'password'
// },
//   Account.authenticate()
// ));
// passport.serializeUser(Account.serializeUser());
// passport.deserializeUser(Account.deserializeUser());


// api routes
app.use('/api', routes);

//let port = process.env.PORT || 3000;

import db from './model';
const Role = db.role;

db.mongoose
  .connect(`mongodb://${dbConfig.HOST}:${dbConfig.PORT}/${dbConfig.DB}`, {
    useNewUrlParser: true,
    useUnifiedTopology: true
  })
  .then(() => {
    console.log("Successfully connect to MongoDB.");
    // console.log("also printing to check");
    initial();
  })
  .catch(err => {
    console.error("Connection error", err);
    process.exit();
  });

function initial() {
  Role.estimatedDocumentCount((err, count) => {
    if (!err && count === 0) {
      new Role({
        name: "Buyer"
      }).save(err => {
        if (err) {
          console.log("error", err);
        }

        console.log("added 'Buyer' to roles collection");
      });

      new Role({
        name: "Investor"
      }).save(err => {
        if (err) {
          console.log("error", err);
        }

        console.log("added 'Investor' to roles collection");
      });

      new Role({
        name: "Realtor"
      }).save(err => {
        if (err) {
          console.log("error", err);
        }

        console.log("added 'Realtor' to roles collection");
      });
    }
  });
}

import myFunc from './routes/auth.routes';
myFunc(app);
import Func2 from './routes/user.routes';
Func2(app);

// let port = 8080
app.server.listen(config.port);
console.log(`Started on port ${app.server.address().port}`);

export default app;
// kill -9 $(lsof -t -i:8080)