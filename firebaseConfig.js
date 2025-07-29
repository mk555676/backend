// // firebaseConfig.js
// import firebase from 'firebase/app';
// import 'firebase/database'; // Import Firebase Realtime Database

// const firebaseConfig = {
//     apiKey: "AIzaSyDaiZ8koJUUpW0msQgjZdhoK8qyZwSN0vU",
//     authDomain: "voiceorderapp.firebaseapp.com",
//     databaseURL: "https://voiceorderapp-default-rtdb.firebaseio.com",
//     projectId: "voiceorderapp",
//     storageBucket: "voiceorderapp.appspot.com",
//     messagingSenderId: "815720036743",
//     appId: "1:815720036743:web:22eac53ec4293d6769bb22"
// };

// if (!firebase.apps.length) {
//   firebase.initializeApp(firebaseConfig);
// }

// const database = firebase.database();

// export default database;

// firebaseConfig.js
// Import necessary Firebase modules for the modular SDK
import firebase from 'firebase/compat/app';
import 'firebase/compat/firestore';
import 'firebase/compat/database';

// Firebase configuration object
const firebaseConfig = {
    apiKey: "AIzaSyBiXZ2XwaJ9FwzB_1ju-0FJQzaSaUBFJGw",
    authDomain: "speaknorder.firebaseapp.com",
    projectId: "speaknorder",
    storageBucket: "speaknorder.appspot.com",
    messagingSenderId: "715190953183",
    appId: "1:715190953183:web:3d9df5427aa793018df56a"
};

if (!firebase.apps.length) {
    firebase.initializeApp(firebaseConfig);
  }
  
  const firestore = firebase.firestore();
  const database = firebase.database();
  
  export { firestore, database };

