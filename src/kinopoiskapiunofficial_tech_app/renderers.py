from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer


class UTF8JSONRenderer(JSONRenderer):
    """Преобразует непонятный набор символов в читаемый текст"""

    #def get_indent(self, accepted_media_type, renderer_context):
    #    
    #    return {
    #        "ensure_ascii": False, # отключаем экранирование не-ASCII символов
    #        "indent": 4 if self.compact else None, # форматируем вывод с отступами
    #    }
    #def render(self, data, accepted_media_type=None, renderer_context=None):
    #    json_dumps_params = {
    #        "ensure_ascii": False, # отключаем экранирование не-ASCII символов
    #        "indent": 4, # форматируем вывод с отступами
    #    }
    #    return super().render(data, accepted_media_type, renderer_context, **{
    #        "json_dumps_params": json_dumps_params
    #    })
    json_dumps_params = {
        "ensure_ascii": False, # отключаем экранирование не-ASCII символов
        "indent": 4, # форматируем вывод с отступами
    }


class UTF8BrowsableAPIRenderer(BrowsableAPIRenderer):
    """Преобразует непонятный набор символов из поля 'Факты' (и не только) в читаемый текст"""

    def get_context(self, data, accepted_media_type, renderer_context):
        
        context = super().get_context(data, accepted_media_type, renderer_context)
        
        if "content" in context and isinstance(context["content"], dict):
            context["content"] = json.dumps(context["content"], ensure_ascii=False, indent=4) # отключаем экранирование не-ASCII символов (JSON-данных) в форме
        
        return context
