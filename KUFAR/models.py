from dataclasses import dataclass, field


@dataclass(slots=True)
class Notebook:
    link: str
    title: str = ''
    price: float = 0.0
    description: str = ''
    producer: str = ''
    diagonal: str = ''
    resolution: str = ''
    os: str = ''
    processor: str = ''
    ram: str = ''
    video_card: str = ''
    hdd_type: str = ''
    hdd_volume: str = ''
    battery: str = ''
    condition: str = ''
    image: list = field(default_factory=list)

