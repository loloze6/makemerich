import backtrader as bt

class DelayedPrice(bt.Indicator):
    lines = ('delayed_price',)
    params = (
        ('delay', 30),
    )

    plotinfo = dict(subplot=False)

    plotlines = dict(
        delayed_price=dict(
            _name='Delayed Price',
            color='blue',
            linestyle='--',
            linewidth=1,
            marker='o',
            _fill_lt=(25000, 'red'),
            _fill_gt=(25000, 'green'),
        ),
    )

    def next(self):
        self.lines.delayed_price[0] = self.data.close[-self.p.delay]
    

