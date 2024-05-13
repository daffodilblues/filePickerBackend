class BaseTransformation:
    def apply(self, content):
        raise NotImplementedError("Each transformation must implement the 'apply' method.")

class ToUppercase(BaseTransformation):
    def apply(self, content):
        return content.upper()
    
class Summarize(BaseTransformation):
    def apply(self, content):
        return content

class TransformationManager:
    def __init__(self):
        self.transformations = [ToUppercase(), Summarize()]

    def should_apply_transform(self, mime_type):
        return mime_type == "application/vnd.google-apps.document"

    def apply_transformations(self, mime_type, content):
        if not self.should_apply_transform(mime_type):
            return content

        transformed_content = content
        for transformation in self.transformations:
            transformed_content = transformation.apply(transformed_content)
        
        return transformed_content

