from pydantic import BaseModel


class FramePreprocessor(BaseModel):
    """
    FramePreprocessor is a decoupled Frame Preprocessor that processes each from
    camera ingestion before passing it to the model for inference.
    It was decoupled to have flexibility in testing new models, params, and so on.
    The method process frame will handle all config passed to it which will be called in FramePreprocessor.
    """