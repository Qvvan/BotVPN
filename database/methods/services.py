class ServiceMethods:
    def __init__(self, spreadsheet):
        self.spreadsheet = spreadsheet

    def get_services(self):
        worksheet = self.spreadsheet.worksheet('Services')
        services = worksheet.get_all_records()
        return services
