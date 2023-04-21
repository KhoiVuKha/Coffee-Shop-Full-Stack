export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:3000', // the running FLASK api server url
  auth0: {
    url: 'khoivu.us', // the auth0 domain prefix
    audience: 'coffee-shop', // the audience set for the auth0 app
    clientId: 'HIe2Ze8Cw85Czmb0CLDUqFboazMPPXeN', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:8100', // the base url of the running ionic application. 
  }
};
