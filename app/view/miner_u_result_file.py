from dataclasses import dataclass

@dataclass
class MinerUResultFile:
    md_file_id: str
    middle_file_id: str
    content_list_file_id: str  # 可以设置默认值


@dataclass
class SOfficeResultFile:
    pdf_file_id: str