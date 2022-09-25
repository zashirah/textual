from ast import Import
import asyncio
import aioboto3

# from rich.json import JSON
from rich.text import Text

from textual.app import App, ComposeResult
from textual import layout
from textual.widgets import Static, TextInput

from textual.widgets import Button, Static

from credentials import ACCESS_KEY_ID, SECRET_ACCESS_KEY

class S3BrowserApp(App):

   def compose(self) -> ComposeResult:
      yield layout.Vertical(
            layout.Horizontal(
               TextInput(placeholder="Search for a word", id="input"), 
               Button("Get Objects", variant="success", id="get_objects"),
               id="search"
            ),
            layout.Vertical(
               Static("Bucket: ", id="bucket_result"),
               Static("Bucket Objects: ", id="object_results"), 
               id="results-container"
            )
         )
   

   async def on_button_pressed(self, event: Button.Pressed) -> None:
      if event.button.id == "get_objects":
         self.query_one("#object_results", Static).update(Text(f'Bucket:'))
         self.query_one("#object_results", Static).update(Text(f'Bucket Objects:'))

         asyncio.create_task(self.get_bucket_objects())


   async def get_bucket_objects(self) -> None:
      session = aioboto3.Session()
      async with session.resource(
         "s3",
         aws_access_key_id=ACCESS_KEY_ID,
         aws_secret_access_key=SECRET_ACCESS_KEY
      ) as s3:
         bucket_object = await s3.Bucket(self.query_one(TextInput).value)
         self.query_one("#bucket_result", Static).update(Text(f'Bucket: {bucket_object}'))

         result = ''
         async for s3_object in bucket_object.objects.all():
            if s3_object:
               result+=f"\n\t- {str(s3_object.key  )}"

         self.query_one(
            "#object_results", 
            Static
         ).update(Text(f'Bucket Objects: {result}'))


app = S3BrowserApp(css_path="s3_browser.css")
if __name__ == "__main__":
   app.run()