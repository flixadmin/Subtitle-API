from requests import post

KEY = 'xicGZDZAN1lUrOLpZIkWNh9X9daztE__'

def createPaste(text:str):
    r = post('https://pastebin.com/api/api_post.php', data=dict(api_dev_key=KEY, api_option='paste', api_paste_code=text))
    return r.text.strip().replace('.com/', '.com/raw/')



if __name__ == '__main__':
    print(createPaste('Hello, world! This is a test paste.'))


