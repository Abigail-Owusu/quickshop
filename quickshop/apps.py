# from django.apps import AppConfig
# from django.apps import apps


# # class QuickShopConfig(AppConfig):
# #     default_auto_field = 'django.db.models.BigAutoField'
# #     name = 'quickshop'

# #     def ready(self):
# #         # Delayed import to avoid import-time issues
# #         from .permissions import create_custom_permissions

# #         # Only call the function if it's safe to do so
# #         if not self.apps.ready:
# #             create_custom_permissions()



# class QuickShopConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'quickshop'

#     def ready(self):
#         # Delayed import to avoid import-time issues
#         from .permissions import create_custom_permissions

#         # Check if the app registry is fully populated
#         if apps.ready and not self.models_ready and self.ready:
#             # Only call the function if it's safe to do so
#             create_custom_permissions()
