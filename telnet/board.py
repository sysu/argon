class BaseBoardFrame(BaseAuthedFrame):


    def setup(self, default, loader, counter):
        self._table = self.load(FinitePagedTable, loader,
                                self._wrapper_li, counter, default,
                                start_line=self._TABEL_START_LINE,
                                height=self._TABEL_HEIGHT)
        
                                
