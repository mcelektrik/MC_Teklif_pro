from PySide6.QtCore import Qt, QAbstractTableModel, Signal

class OfferItemsModel(QAbstractTableModel):
    def __init__(self, items=None):
        super().__init__()
        self.items = items or []
        self.headers = ["Açıklama", "Miktar", "Birim", "Birim Fiyat", "KDV %", "İskonto %", "Tutar"]

    def rowCount(self, parent=None):
        return len(self.items)

    def columnCount(self, parent=None):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        item = self.items[index.row()]
        col = index.column()
        
        if role == Qt.DisplayRole:
            if col == 0: return item.description
            elif col == 1: return str(item.quantity)
            elif col == 2: return item.unit
            elif col == 3: return f"{item.unit_price:.2f}"
            elif col == 4: return str(item.vat_rate)
            elif col == 5: return str(item.discount_percent)
            elif col == 6: return f"{item.total_price:.2f}"
            
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

    def add_item(self, item):
        self.beginInsertRows(self.index(len(self.items), 0), len(self.items), len(self.items))
        self.items.append(item)
        self.endInsertRows()

    def remove_item(self, row):
        self.beginRemoveRows(self.index(row, 0), row, row)
        self.items.pop(row)
        self.endRemoveRows()
        
    def clear(self):
        self.beginResetModel()
        self.items = []
        self.endResetModel()
