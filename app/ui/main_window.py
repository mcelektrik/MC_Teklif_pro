
def _fix_utf8(text):
    try:
        return text.encode("latin1").decode("utf-8")
    except:
        return text
import sys
import logging
from types import SimpleNamespace
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLineEdit, QTextEdit, QTableView, QPushButton, QLabel, 
    QComboBox, QSpinBox, QDoubleSpinBox, QGroupBox, QSplitter,
    QMessageBox, QProgressDialog
)
from sqlalchemy.orm import object_session
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QAction

from app.core.db import get_db, init_db, SessionLocal
from app.core.schema import Offer, OfferItem, Customer, AppConfig
from app.core.services import generate_offer_no, calculate_offer_totals
from app.core.settings import AppSettings
from app.ui.models import OfferItemsModel
from app.ui.dialogs import SettingsDialog
from app.pdf.render import generate_pdf

logger = logging.getLogger(__name__)

class PdfWorker(QThread):
    finished = Signal(str)
    error = Signal(str)
    
    def __init__(self, offer_id, settings):
        super().__init__()
        self.offer_id = offer_id
        self.settings = settings
        
    def run(self):
        db = SessionLocal()
        try:
            from sqlalchemy.orm import joinedload
            # Eager load relationships
            offer = db.query(Offer).options(
                joinedload(Offer.customer),
                joinedload(Offer.items)
            ).filter(Offer.id == self.offer_id).first()
            
            if not offer:
                raise Exception("Offer not found")
                
            path = generate_pdf(offer, self.settings)
            self.finished.emit(str(path))
        except Exception as e:
            logger.exception('DEBUG_SAVE_DRAFT_EXCEPTION')
            logger.error(f"PDF Generation Error: {e}")
            self.error.emit(str(e))
        finally:
            db.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MC_Teklif_Pro")
        self.resize(1200, 800)
        
        self.db = SessionLocal()
        
        # Load Settings
        self.settings = self.load_settings()
        
        self.setup_ui()
        self.load_draft()

    def load_settings(self):
        settings = {}
        try:
            configs = self.db.query(AppConfig).all()
            for config in configs:
                settings[config.key] = config.value
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
        return settings

    def save_settings(self, new_settings):
        try:
            for key, value in new_settings.items():
                config = self.db.query(AppConfig).filter_by(key=key).first()
                if not config:
                    config = AppConfig(key=key, value=value)
                    self.db.add(config)
                else:
                    config.value = value
                self.settings[key] = value
            self.db.commit()
            logger.info('DEBUG_SAVE_DRAFT_COMMIT_OK offer_id=%s', getattr(self.current_offer,'id',None))
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            QMessageBox.critical(self, "Hata", f"Ayarlar kaydedilemedi: {e}")

    def setup_ui(self):
        # Menu Bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Dosya")
        
        settings_action = QAction("Ayarlar", self)
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)
        
        exit_action = QAction("AAAaAAasAAAAAzAasAkAAaAaAAAAaAaA", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left Panel: Customer & Offer Info
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Customer Group
        cust_group = QGroupBox("MÜŞTERİ BİLGİLERİ")
        cust_form = QFormLayout()
        self.cust_name = QLineEdit()
        self.cust_address = QTextEdit()
        self.cust_address.setMaximumHeight(60)
        self.cust_tax_office = QLineEdit()
        self.cust_tax_no = QLineEdit()
        
        cust_form.addRow("Ad / 'nvan:", self.cust_name)
        cust_form.addRow("Adres:", self.cust_address)
        cust_form.addRow("Vergi Dairesi:", self.cust_tax_office)
        cust_form.addRow("Vergi No:", self.cust_tax_no)
        cust_group.setLayout(cust_form)
        left_layout.addWidget(cust_group)
        
        # Offer Meta Group
        meta_group = QGroupBox("Teklif Detaylar")
        meta_form = QFormLayout()
        self.offer_no = QLineEdit()
        self.offer_no.setReadOnly(True)
        self.offer_currency = QComboBox()
        self.offer_currency.addItems(["TRY", "USD", "EUR"])
        self.offer_vat_included = QComboBox()
        self.offer_vat_included.addItems(["KDV Dahil", "KDV Hari'ç"])
        
        meta_form.addRow("Teklif No:", self.offer_no)
        meta_form.addRow("Para Birimi:", self.offer_currency)
        meta_form.addRow("KDV Durumu:", self.offer_vat_included)
        meta_group.setLayout(meta_form)
        left_layout.addWidget(meta_group)
        
        left_layout.addStretch()
        splitter.addWidget(left_panel)
        
        # Right Panel: Items & Totals
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Item Input
        item_input_group = QGroupBox("Yeni Kalem Ekle")
        item_input_layout = QHBoxLayout()
        
        self.item_desc = QLineEdit()
        self.item_qty = QDoubleSpinBox()
        self.item_qty.setValue(1)
        self.item_unit = QComboBox()
        self.item_unit.addItems(["Adet", "Metre", "Kg", "Saat", "G'ün"])
        self.item_unit.setEditable(True)
        self.item_price = QDoubleSpinBox()
        self.item_price.setDecimals(2)
        self.item_price.setRange(0, 999999999)
        self.item_price.setSingleStep(1)
        self.item_price.setPrefix("? ")
        self.item_price.setMaximum(999999999)
        self.item_vat = QDoubleSpinBox()
        self.item_vat.setValue(20)
        self.item_disc = QDoubleSpinBox()
        self.item_disc.setValue(0)
        
        add_btn = QPushButton("Ekle")
        add_btn.clicked.connect(self.add_item)
        
        item_input_layout.addWidget(self.item_desc, 3)
        item_input_layout.addWidget(self.item_qty, 1)
        item_input_layout.addWidget(self.item_unit, 1)
        item_input_layout.addWidget(self.item_price, 1)
        item_input_layout.addWidget(QLabel("KDV%"), 0)
        item_input_layout.addWidget(self.item_vat, 1)
        item_input_layout.addWidget(QLabel("sk%"), 0)
        item_input_layout.addWidget(self.item_disc, 1)
        item_input_layout.addWidget(add_btn, 1)
        
        item_input_group.setLayout(item_input_layout)
        right_layout.addWidget(item_input_group)
        
        # Items Table
        self.items_model = OfferItemsModel()
        self.items_table = QTableView()
        self.items_table.setModel(self.items_model)
        self.items_table.setSelectionBehavior(QTableView.SelectRows)
        right_layout.addWidget(self.items_table)
        
        # Delete Button
        del_btn = QPushButton("SEÇİLİ SATIR SİL")
        del_btn.clicked.connect(self.delete_item)
        right_layout.addWidget(del_btn)
        
        # Totals
        totals_group = QGroupBox("Toplamlar")
        totals_form = QFormLayout()
        self.lbl_subtotal = QLabel("0.00")
        self.lbl_vat = QLabel("0.00")
        self.lbl_grand = QLabel("0.00")
        self.lbl_grand.setStyleSheet("font-weight: bold; font-size: 14pt; color: red;")
        
        totals_form.addRow("Ara Toplam:", self.lbl_subtotal)
        totals_form.addRow("KDV Toplam:", self.lbl_vat)
        totals_form.addRow("GENEL TOPLAM:", self.lbl_grand)
        totals_group.setLayout(totals_form)
        right_layout.addWidget(totals_group)
        
        # Actions
        actions_layout = QHBoxLayout()
        save_btn = QPushButton("Kaydet (Taslak)")
        save_btn.clicked.connect(self.save_draft)
        pdf_btn = QPushButton("PDF Olutur")
        pdf_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        pdf_btn.clicked.connect(self.create_pdf)
        
        actions_layout.addWidget(save_btn)
        actions_layout.addWidget(pdf_btn)
        right_layout.addLayout(actions_layout)
        
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 800])

    def open_settings(self):
        dlg = SettingsDialog(self, self.settings)
        if dlg.exec():
            new_settings = dlg.get_settings()
            self.save_settings(new_settings)

    def add_item(self):
        desc = self.item_desc.text()
        if not desc:
            return
            
        item = OfferItem(
            description=desc,
            quantity=self.item_qty.value(),
            unit=self.item_unit.currentText(),
            unit_price=self.item_price.value(),
            vat_rate=self.item_vat.value(),
            discount_percent=self.item_disc.value(),
            total_price=0 # Will be calculated
        )
        
        # Calculate item total price for display immediately
        # But real calculation happens in `update_totals`
        self.items_model.add_item(item)
        self.item_desc.clear()
        self.update_totals()

    def delete_item(self):
        indexes = self.items_table.selectionModel().selectedRows()
        if indexes:
            self.items_model.remove_item(indexes[0].row())
            self.update_totals()

    def update_totals(self):
        # Create a temporary offer object to use the service logic
        temp_offer = Offer(
            include_vat=(self.offer_vat_included.currentIndex() == 0),
            items=self.items_model.items
        )
        calculate_offer_totals(temp_offer)
        
        currency = self.offer_currency.currentText()
        self.lbl_subtotal.setText(f"{temp_offer.sub_total:,.2f} {currency}")
        self.lbl_vat.setText(f"{temp_offer.vat_total:,.2f} {currency}")
        self.lbl_grand.setText(f"{temp_offer.grand_total:,.2f} {currency}")
        
        # Refresh table to show updated item totals
        self.items_model.layoutChanged.emit()

    def load_draft(self):
        # Load the latest draft offer or create a new one
        try:
            draft = self.db.query(Offer).filter_by(status="DRAFT").order_by(Offer.updated_at.desc()).first()
            
            if draft:
                self.current_offer = draft
                # Populate UI
                if draft.customer:
                    self.cust_name.setText(draft.customer.name)
                    self.cust_address.setText(draft.customer.address)
                    self.cust_tax_office.setText(draft.customer.tax_office)
                    self.cust_tax_no.setText(draft.customer.tax_no)
                    if hasattr(self, 'cust_contact'):
                        self.cust_contact.setText(getattr(draft.customer, 'contact_person', '') or getattr(draft.customer, 'contact', '') or '')
                
                self.offer_no.setText(draft.offer_no)
                self.offer_currency.setCurrentText(draft.currency)
                self.offer_vat_included.setCurrentIndex(0 if draft.include_vat else 1)
                
                self.items_model.items = list(draft.items)
                self.items_model.layoutChanged.emit()
                self.update_totals()
            else:
                # New Offer
                self.current_offer = Offer()
                self.offer_no.setText(generate_offer_no(self.db))
        except Exception as e:
            logger.error(f"Failed to load draft: {e}")
            self.current_offer = Offer()
            self.offer_no.setText(_fix_utf8("\1"))

    def save_draft(self):
        try:
            logger.info('DEBUG_SAVE_DRAFT_ENTER offer_id=%s items_model=%s', getattr(self.current_offer,'id',None), len(getattr(self.items_model,'items',[]) or []))
            # ensure current_offer is in session early (prevents SAWarning on OfferItem.offer)
            try:
                _os = object_session(self.current_offer)
            except Exception:
                _os = None
            if _os is None:
                self.db.add(self.current_offer)
                self.db.flush()  # allocate PK

            # Create or Update Customer
            if not self.cust_name.text():
                QMessageBox.warning(self, "Hata", "Müşteri adı boş olamaz.")
                return False

            customer = None
            if self.current_offer.customer_id:
                customer = self.db.query(Customer).get(self.current_offer.customer_id)
            
            if not customer:
                customer = Customer()
                self.db.add(customer)
                
            customer.name = self.cust_name.text()
            customer.address = self.cust_address.toPlainText()
            customer.tax_office = self.cust_tax_office.text()
            customer.tax_no = self.cust_tax_no.text()
            # best-effort: persist 'Yetkili Kişi' if field exists
            if hasattr(customer, 'contact_person') and hasattr(self, 'cust_contact'):
                customer.contact_person = self.cust_contact.text()
            elif hasattr(customer, 'contact') and hasattr(self, 'cust_contact'):
                customer.contact = self.cust_contact.text()

            self.db.flush()
            
            # Update Offer
            self.current_offer.customer_id = customer.id
            self.current_offer.offer_no = self.offer_no.text()
            self.current_offer.currency = self.offer_currency.currentText()
            self.current_offer.include_vat = (self.offer_vat_included.currentIndex() == 0)
            self.current_offer.status = "DRAFT"
            
            # Update Items (safe, offer_id-based)
            # ensure offer is in session + has PK
            try:
                _os = object_session(self.current_offer)
            except Exception:
                _os = None
            if _os is None:
                self.db.add(self.current_offer)
                self.db.flush()
            
            # UI_DETACH_SNAPSHOT: break ORM links before bulk delete (prevents ObjectDeletedError in Qt model)
            
            ui_items = []
            
            for _it in (self.items_model.items or []):
            
                ui_items.append(SimpleNamespace(
            
                    description=getattr(_it,'description',''),
            
                    quantity=getattr(_it,'quantity',0),
            
                    unit=getattr(_it,'unit',''),
            
                    unit_price=getattr(_it,'unit_price',0),
            
                    vat_rate=getattr(_it,'vat_rate',0),
            
                    discount_percent=getattr(_it,'discount_percent',0),
            
                ))
            
            self.items_model.items = ui_items
            
            try:
            
                self.items_model.layoutChanged.emit()
            
            except Exception:
            
                pass
            
            # delete old items in DB to prevent accumulation
            self.db.query(OfferItem).filter(OfferItem.offer_id == self.current_offer.id).delete(synchronize_session=False)
            self.db.expire_all()
            
            item_n = 0
            for item in (self.items_model.items or []):
                new_item = OfferItem(
                    offer_id=self.current_offer.id,
                    description=item.description,
                    quantity=item.quantity,
                    unit=item.unit,
                    unit_price=item.unit_price,
                    vat_rate=item.vat_rate,
                    discount_percent=item.discount_percent
                )
                self.db.add(new_item)
                item_n += 1
            logger.info('DEBUG_SAVE_ITEMS_WRITTEN offer_id=%s n=%s', self.current_offer.id, item_n)
            
            calculate_offer_totals(self.current_offer)
            
            if not self.current_offer.id:
                self.db.add(self.current_offer)
                
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save draft: {e}")
            QMessageBox.critical(self, "Hata", f"Kaydedilemedi: {e}")
            self.db.rollback()
            return False

    def create_pdf(self):
        if not self.save_draft():
            return

        self.progress = QProgressDialog("PDF oluturuluyor...", None, 0, 0, self)
        self.progress.setWindowModality(Qt.WindowModal)
        self.progress.show()
        
        # Pass ID instead of object
        self.worker = PdfWorker(self.current_offer.id, self.settings)
        self.worker.finished.connect(self.on_pdf_finished)
        self.worker.error.connect(self.on_pdf_error)
        self.worker.start()

    def on_pdf_finished(self, path):
        self.progress.close()
        QMessageBox.information(self, "Baarl", f"PDF oluturma tamamland:\n{path}")
        # Open PDF
        try:
            import os
            os.startfile(path)
        except Exception as e:
            logger.error(f"Failed to open PDF: {e}")

    def on_pdf_error(self, error):
        self.progress.close()
        QMessageBox.critical(self, "Hata", f"PDF oluturulamad:\n{error}")

    def closeEvent(self, event):
        # Auto-save on close?
        # Maybe ask? Or just save draft silently?
        # Requirement says: "Autosave"
        self.save_draft()
        self.db.close()
        event.accept()


    def update_currency_symbol(self):
        symbol_map = {
            "TL": "? ",
            "USD": "$ ",
            "EUR": " "
        }
        current = self.currency_combo.currentText()
        # currency prefix bind
        try:
            self.currency_combo.currentTextChanged.connect(lambda _=None: self.update_currency_symbol())
            self.update_currency_symbol()
        except Exception:
            pass
        self.item_price.setPrefix(symbol_map.get(current, "? "))

