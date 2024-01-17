from dataclasses import dataclass


@dataclass
class RequestCmd:
    name : str 
    type : str 
    id   : int 
    

    def __str__(self) -> str:
        return f'{self.name}_{self.id}_{self.type}'