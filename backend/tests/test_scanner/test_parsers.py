from scanner.parsers.connection_string import ConnectionStringParser


class TestConnectionStringParser:
    def setup_method(self):
        self.parser = ConnectionStringParser()

    def test_parse_oracle_jdbc(self):
        url = "jdbc:oracle:thin:@10.0.2.20:1521/PRODDB"
        result = self.parser.parse_jdbc(url)
        assert result["target_host"] == "10.0.2.20"
        assert result["target_port"] == 1521
        assert result["database"] == "PRODDB"
        assert result["protocol"] == "oracle"

    def test_parse_postgresql_jdbc(self):
        url = "jdbc:postgresql://10.0.2.25:5432/analytics"
        result = self.parser.parse_jdbc(url)
        assert result["target_host"] == "10.0.2.25"
        assert result["target_port"] == 5432
        assert result["database"] == "analytics"
        assert result["protocol"] == "postgresql"

    def test_parse_mysql_jdbc(self):
        url = "jdbc:mysql://dbhost:3306/mydb"
        result = self.parser.parse_jdbc(url)
        assert result["target_host"] == "dbhost"
        assert result["target_port"] == 3306
        assert result["database"] == "mydb"
        assert result["protocol"] == "mysql"

    def test_parse_sqlserver_jdbc(self):
        url = "jdbc:sqlserver://10.0.5.10:1433;databaseName=ReportDB"
        result = self.parser.parse_jdbc(url)
        assert result["target_host"] == "10.0.5.10"
        assert result["target_port"] == 1433
        assert result["protocol"] == "sqlserver"
