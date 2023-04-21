export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'khoivu.us.auth0.com', // the auth0 domain prefix
    audience: 'coffee-shop', // the audience set for the auth0 app
    clientId: '6440ef306f6220401c27861d', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:8100', // the base url of the running ionic application. 
  }
};
