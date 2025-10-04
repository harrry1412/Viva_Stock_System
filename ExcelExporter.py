from PyQt5.QtCore import QRunnable, pyqtSignal, QObject
from PIL import Image as PilImage
import xlsxwriter
import os
import shutil

class ExportSignals(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

class ExcelExporter(QRunnable):
    def __init__(self, db_manager, filtered_suppliers, selected_file, include_images):
        super().__init__()
        self.db_manager = db_manager
        self.filtered_suppliers = filtered_suppliers
        self.selected_file = selected_file
        self.include_images = include_images
        self.signals = ExportSignals()

    def run(self):
        try:
            # Define the image directory path and temporary folder path variables
            image_directory = "//VIVA303-WORK/Viva店面共享/StockImg/"
            temp_directory = "temp"

            # Create the temporary folder if it doesn't exist
            if not os.path.exists(temp_directory):
                os.makedirs(temp_directory)

            # Get the data to be exported (retrieved from the database)
            selected_suppliers = self.filtered_suppliers
            rows_to_export = self.db_manager.fetch_rugs()

            # Specify custom column order
            column_order = ['Image', 'Model', 'Quantity', 'Type', 'Supplier', 'WLevel', 'Remarks']

            # Sort the data to meet the requirements
            rows_to_export.sort(key=lambda x: (x[2], x[1], x[0]))

            # Create a new Excel workbook
            workbook = xlsxwriter.Workbook(self.selected_file)
            default_sheet = workbook.add_worksheet('All Suppliers')

            # Add column headers
            default_sheet.write_row(0, 0, column_order)

            # Set column width and row height for square cells
            cell_size = 60  # Cell size 60x60 pixels
            if self.include_images:
                default_sheet.set_column('A:A', cell_size / 7.2)  # Excel column width unit is approximately 1/7.2 of a character width
                for row_idx in range(1, len(rows_to_export) + 1):
                    default_sheet.set_row(row_idx, cell_size)  # Set row height to 60 pixels

            # Populate the default worksheet with data
            for row_idx, row in enumerate(rows_to_export, start=1):
                row_data = [row[5], row[0], row[1], row[3], row[2], row[6], row[4]]
                default_sheet.write_row(row_idx, 1, row_data[1:])

                if self.include_images:
                    img_path = f"{image_directory}{row[5]}"
                    try:
                        with PilImage.open(img_path) as img:
                            # Calculate scaling ratio to maintain the image's aspect ratio and fit within the 60x60 cell
                            width_ratio = cell_size / img.width
                            height_ratio = cell_size / img.height
                            scale_ratio = min(width_ratio, height_ratio)
                            new_width = int(img.width * scale_ratio)
                            new_height = int(img.height * scale_ratio)
                            img = img.resize((new_width, new_height), PilImage.LANCZOS)

                            # Save the temporary image in the temp folder
                            temp_path = os.path.join(temp_directory, f"temp_{row[5]}")
                            img.save(temp_path)

                            # Insert the image and lock it to the cell
                            default_sheet.insert_image(row_idx, 0, temp_path, {
                                'x_scale': 1,
                                'y_scale': 1,
                                'x_offset': int((cell_size - new_width) / 2),
                                'y_offset': int((cell_size - new_height) / 2),
                                'object_position': 1  # Image fixed to the cell, hidden with the cell
                            })

                    except Exception as e:
                        pass

            # Create individual worksheets for each supplier
            suppliers = set(row[2] for row in rows_to_export)
            for supplier in suppliers:
                sheet = workbook.add_worksheet(supplier)
                sheet.write_row(0, 0, column_order)

                # Set column width and row height for square cells
                if self.include_images:
                    sheet.set_column('A:A', cell_size / 7.2)
                    for row_idx in range(1, len(rows_to_export) + 1):
                        sheet.set_row(row_idx, cell_size)

                supplier_data = [row for row in rows_to_export if row[2] == supplier]
                for row_idx, row in enumerate(supplier_data, start=1):
                    row_data = [row[5], row[0], row[1], row[3], row[2], row[6], row[4]]
                    sheet.write_row(row_idx, 1, row_data[1:])

                    if self.include_images:
                        img_path = f"{image_directory}{row[5]}"
                        try:
                            with PilImage.open(img_path) as img:
                                width_ratio = cell_size / img.width
                                height_ratio = cell_size / img.height
                                scale_ratio = min(width_ratio, height_ratio)
                                new_width = int(img.width * scale_ratio)
                                new_height = int(img.height * scale_ratio)
                                img = img.resize((new_width, new_height), PilImage.LANCZOS)

                                temp_path = os.path.join(temp_directory, f"temp_{row[5]}")
                                img.save(temp_path)

                                sheet.insert_image(row_idx, 0, temp_path, {
                                    'x_scale': 1,
                                    'y_scale': 1,
                                    'x_offset': int((cell_size - new_width) / 2),
                                    'y_offset': int((cell_size - new_height) / 2),
                                    'object_position': 1
                                })

                        except Exception as e:
                            pass

            workbook.close()

            # Delete the temporary files and folder
            shutil.rmtree(temp_directory)

            # Emit the finished signal
            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit(str(e))
