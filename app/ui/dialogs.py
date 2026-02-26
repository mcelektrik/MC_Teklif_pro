from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox, 
    QFileDialog, QPushButton, QHBoxLayout, QLabel
)
from app.core.settings import AppSettings

class SettingsDialog(QDialog):
    def __init__(self, parent=None, settings_dict=None):
        super().__init__(parent)
        self.setWindowTitle("Ayarlar")
        self.settings = settings_dict or {}
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.company_name = QLineEdit(self.settings.get(AppSettings.COMPANY_NAME, ""))
        self.company_address = QLineEdit(self.settings.get(AppSettings.COMPANY_ADDRESS, ""))
        self.company_tax = QLineEdit(self.settings.get(AppSettings.COMPANY_TAX_NO, ""))
        self.company_phone = QLineEdit(self.settings.get(AppSettings.COMPANY_PHONE, ""))
        self.company_iban = QLineEdit(self.settings.get(AppSettings.COMPANY_IBAN, ""))
        
        # Logo Path
        self.logo_path = QLineEdit(self.settings.get(AppSettings.LOGO_PATH, ""))
        logo_btn = QPushButton("Seç")
        logo_btn.clicked.connect(lambda: self.select_file(self.logo_path))
        logo_layout = QHBoxLayout()
        logo_layout.addWidget(self.logo_path)
        logo_layout.addWidget(logo_btn)
        
        # Signature Path
        self.sign_path = QLineEdit(self.settings.get(AppSettings.SIGNATURE_PATH, ""))
        sign_btn = QPushButton("Seç")
        sign_btn.clicked.connect(lambda: self.select_file(self.sign_path))
        sign_layout = QHBoxLayout()
        sign_layout.addWidget(self.sign_path)
        sign_layout.addWidget(sign_btn)
        
        form_layout.addRow("Firma Adı:", self.company_name)
        form_layout.addRow("Adres:", self.company_address)
        form_layout.addRow("Vergi No:", self.company_tax)
        form_layout.addRow("Telefon:", self.company_phone)
        form_layout.addRow("IBAN:", self.company_iban)
        form_layout.addRow("Logo:", logo_layout)
        form_layout.addRow("İmza/Kaşe:", sign_layout)
        
        layout.addLayout(form_layout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
    def select_file(self, line_edit):
        path, _ = QFileDialog.getOpenFileName(self, "Dosya Seç", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            line_edit.setText(path)
            
    def get_settings(self):
        return {
            AppSettings.COMPANY_NAME: self.company_name.text(),
            AppSettings.COMPANY_ADDRESS: self.company_address.text(),
            AppSettings.COMPANY_TAX_NO: self.company_tax.text(),
            AppSettings.COMPANY_PHONE: self.company_phone.text(),
            AppSettings.COMPANY_IBAN: self.company_iban.text(),
            AppSettings.LOGO_PATH: self.logo_path.text(),
            AppSettings.SIGNATURE_PATH: self.sign_path.text(),
        }
