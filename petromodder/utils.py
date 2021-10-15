import pathlib
import pandas as pd
import numpy as np
from .logging import logger
class Utils:
    @staticmethod
    def path_checker(path):
        if isinstance(path, pathlib.PurePath):
            pass
        elif isinstance(path,str):
            path = pathlib.Path(path)
        else:
            logger.critical("Invalid Path")
        return path
        
    @staticmethod
    def get_version(project_path):
        with (open(project_path / "def//version.pma")) as f:
            for line in f:
                version = line
                version = version[len("Version: "):]
                version = version.strip()        
        supported_version = ["2018","2019", "2020"]
        if version not in supported_version:
            logger.warning(f"Unsupported versions. Supported versions {supported_version}")
        return version
    @staticmethod
    def check_ndim(model_path):
        """Check model dimensions"""
        path = str(model_path)
        if "pm3d" in path:
            ndim = 3
        elif "pm2d" in path:
            ndim = 2
        elif "pm1d" in path:
            ndim = 1
        else:
            logger.critical("Invalud model path")
        return ndim
    @staticmethod
    def read_pmt(fullpath):
        """Parse PetroMod PMT file"""
        with (open(fullpath)) as f:
            for i, line in enumerate(f):
                if line.startswith("Key"):
                    ind = i
                elif line.startswith("Data"):
                    data = i - ind - 1
                    break
        if ind == None or data == None:
            logger.critical("Invalid PMT file")
        df = pd.read_table(fullpath, delimiter="|", header=ind)
        df = df.rename(columns=lambda x: x.strip())
        df = df.iloc[(data):]
        df = df.reset_index(drop=True)
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        df = df.apply(pd.to_numeric, errors="ignore")
        return df
    @staticmethod
    def write_pmt( PM_data_type, df, col_num, headers,version):
        """[summary]
        
        Arguments:
            type {str} -- PM data table type for meta header
            df {DataFrame} -- dats to export
            col_num {int} -- Number of columns in the data table
            headers {list of list} -- List of headers. Last one is format header
        
        Raises:
            Exception: Input col num and header col number mismatch
            Exception: Length of header length mismatch
        
        Returns:
            output {str} -- markdown table in PM format
        
 
        """
        # Make meta header
        version = "c " + PM_data_type + " [PetroMod " + version + "]"
        meta = """c\n{vars}\nc\n""".format(
            length="multi-line", ordinal="second", vars=version
        )
        # Error check col_numbers vs header
        for i in headers:
            if len(i) != col_num:
                raise Exception("Headers and column numbers mismatch")
        # Fix df cell length
        while df.shape[1] > col_num:
            df = df.drop(df.columns[-1], axis=1)
        # max len of all cell and header by column in df
        measurer = np.vectorize(len)
        df_header_len = list(map(len, df.columns))
        max_len_df = measurer(df.values.astype(str)).max(axis=0)
        df_len = list(map(max, max_len_df, df_header_len))
        # PM header and format header length
        head = pd.DataFrame(headers)
        max_header = measurer(head.values.astype(str)).max(axis=0)
        # Make sure df header string length is same as PM header length
        col = list(df.columns)
        for i in range(len(df_len)):
            if df_len[i] > max_header[i]:
                pass
            elif df_len[i] < max_header[i]:
                col[i] = col[i].ljust(max_header[i])
        df.columns = col
        # df to markdown
        a = df.to_markdown()
        # get header from markdon
        b = a.splitlines()[0]
        # Count string len between pipes in header
        def find_all(a_str, sub):
            start = 0
            while True:
                start = a_str.find(sub, start)
                if start == -1:
                    return
                yield start
                start += len(sub)  # use start += 1 to find overlapping matches

        # Index of pipes
        ind = np.array(list(find_all(b, "|")))
        # Length of string in header between pipes
        diff = np.diff(ind) - 1
        diff = diff[1:]
        # Strip header in markdown
        c = a.split("\n", 2)[-1]
        # Loop multiline string to strip first col in markdown
        stripped = ""
        for x in iter(c.splitlines()):
            x_ = x[ind[1] + 2 :]
            stripped = stripped + x_ + "\n"

        def add_header_prop(list_header, size_header):
            out = ""
            for ind, x in enumerate(list_header):
                if len(x) > size_header[ind]:
                    logger.critical("Format error")
                elif len(x) < size_header[ind]:
                    if ind > 0:
                        string = x.center(size_header[ind])
                    else:
                        string = x.ljust(size_header[ind] - 1)
                else:
                    string = x
                string = string + "|"
                out = out + string
            return out

        header = ""
        for i in headers[:-1]:
            h = add_header_prop(i, diff)
            header = header + h + "\n"
        format_header = add_header_prop(headers[-1], diff) + "\n"
        div_1 = "Stop"
        div_1 = div_1.ljust(len(format_header), "-") + "\n"
        div_2 = "c"
        div_2 = div_2.ljust(len(format_header), "-") + "\n"
        output = meta + header + div_1 + format_header + div_2 + stripped
        return output

