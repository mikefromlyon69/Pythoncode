#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os

#import sys to define the path to your tweepy library
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "lib/tweepy"))
import tweepy

#we use the sessions module provided directly by weapp2. In production code make sure to store your secret key in a secure place

from webapp2_extras import sessions

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'yoursecretkey',
}    

class Handler(webapp2.RequestHandler):
    #juste a method to write shorter code
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)


    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))
    

    #again it would be safer to put our consumer key and consumer secret in a secure place 
    def twitterconnect(self):
        consumer_key="yourconsumerkey"
        consumer_secret="yourconsumersecret"
       
        
        return tweepy.OAuthHandler(consumer_key, consumer_secret)
    
    #webapp2 session method
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

    



class OauthHandler(Handler):
    def get(self):

        

        auth = self.twitterconnect()
        #this line makes sure tweepy connects with ssl
        auth.secure = True

        try:    
                #we specify signin with twitter so twitter doesn't ask for permissions everytime
                redirect_url = auth.get_authorization_url(signin_with_twitter=True)
                #we store the request token in a session because we will  need it on the callback
                self.session['request_token'] = (auth.request_token.key,auth.request_token.secret)
                self.redirect(redirect_url)
        except tweepy.TweepError:
                self.write('Error! Failed to get request token.')
                return

#the callback URL where the user is directed after the Twitter log in
class CallBackHandler(Handler):
    def get(self):
        
       
        
        
        
        token = self.session.get('request_token')
       
            
           
        
        #twitter is sending us the oauth verifier as a get paramater
        verifier = self.request.get('oauth_verifier')      
        auth = self.twitterconnect()
        #again make sure to use ssl or it will fail
        auth.secure = True
        if token is not None:
            auth.set_request_token(token[0], token[1])
        else:
            self.write("no token found")
        try:
             auth.get_access_token(verifier)
        except tweepy.TweepError:
            self.write("error")
            return
        
        api = tweepy.API(auth)
        api.verify_credentials()
        if not api:
            self.write("connexion failed")
            return
            
        self.session['username']=api.me().screen_name
        
        self.write("Welcome" + self.session['username'])
        
        
        
            
        
         
        






app = webapp2.WSGIApplication([ ('/tweepyconnection', OauthHandler),('/tweepyconnection/callback.*', CallBackHandler)], debug=True,config=config)