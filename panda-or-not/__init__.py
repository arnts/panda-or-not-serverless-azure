import logging
import azure.functions as func

from fastai.vision import *

def main(req: func.HttpRequest) -> func.HttpResponse:

    path = Path.cwd()
    learn = load_learner(path, 'bears.pkl')

    request_json = req.get_json()
    r = requests.get(request_json['url'])

    if r.status_code == 200:
        temp_image_name = "temp.jpg"        
        with open(temp_image_name, 'wb') as f:
            f.write(r.content)
    else:
        return func.HttpResponse(f"Image download failed, url: {request_json['url']}")

    img = open_image(temp_image_name)
    pred_class, pred_idx, outputs = learn.predict(img)

    return func.HttpResponse(f"request_json['url']: {request_json['url']}, pred_class: {pred_class}")

