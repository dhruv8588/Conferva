from django.contrib.sessions.models import Session

from accounts.models import LoggedInUser

# class OneSessionPerUser:
#     def __init__(self, get_response):
#         self.get_response = get_response
#         # One-time configuration and initialization.

#     def __call__(self, request):
#         # Code to be executed for each request before
#         # the view (and later middleware) are called.
#         if request.user.is_authenticated:
#             current_session_key = request.user.logged_in_user.session_key

#             if current_session_key and current_session_key != request.session.session_key:
#                 Session.objects.get(session_key=current_session_key).delete() 

#             request.user.logged_in_user.session_key = request.session.session_key
#             request.user.logged_in_user.save()

#         response = self.get_response(request)

#         # Code to be executed for each request/response after
#         # the view is called.

#         return response

class OneSessionPerUser:
    # Called only once when the web server starts
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        # if request.user.is_authenticated:
        #     session_key = request.session.session_key

        #     try:
        #         logged_in_user = request.user.logged_in_user
        #         stored_session_key = logged_in_user.session_key
        #         # stored_session_key exists so delete it if it's different
        #         if stored_session_key and stored_session_key != request.session.session_key:
        #             Session.objects.get(session_key=stored_session_key).delete()
        #         request.user.logged_in_user.session_key = request.session.session_key
        #         request.user.logged_in_user.save()
        #     except LoggedInUser.DoesNotExist:
        #         print("hiiii")
        #         LoggedInUser.objects.create(user=request.user, session_key=session_key)


            ##############

        if request.user.is_authenticated:
            current_session_key = request.user.logged_in_user.session_key

            if current_session_key and current_session_key != request.session.session_key:
                Session.objects.get(session_key=current_session_key).delete() 

            request.user.logged_in_user.session_key = request.session.session_key
            request.user.logged_in_user.save()


            # stored_session_key = request.user.logged_in_user.session_key

            # if there is a stored_session_key  in our database and it is
            # different from the current session, delete the stored_session_key
            # session_key with from the Session table
            # if stored_session_key and stored_session_key != request.session.session_key:
            #     Session.objects.get(session_key=stored_session_key).delete()

            # request.user.logged_in_user.session_key = request.session.session_key
            # request.user.logged_in_user.save()

        response = self.get_response(request)

        # This is where you add any extra code to be executed for each request/response after
        # the view is called.
        # For this tutorial, we're not adding any code so we just return the response

        return response
