from quantopian.algorithm import attach_pipeline, pipeline_output
from quantopian.pipeline import Pipeline
from quantopian.pipeline.factors import CustomFactor
from quantopian.pipeline.data.quandl import cboe_vix
        
def initialize(context):
    #Assets
    context.XIV = sid(40516) #XIV - Bullish
    context.UVXY = sid(8554)#UVXY - Bearish or VXX less contango JUST SPY
    context.BND = sid(23921) #Treasury Bonds
    
    #Constants
    context.PIGGY_RATIO = .5  #50% of portfolio is bonds
    context.CASH = 500 #how much cash to keep in portfolio
    context.max_value = context.portfolio.portfolio_value #highest portfolio value
    context.PIGGY = context.max_value*context.PIGGY_RATIO #dollar amount of bonds to hold
    context.holding = "Nothing"
    
    pipe = Pipeline()
    attach_pipeline(pipe, 'my_pipeline')
    pipe.add(GetVIX(inputs=[cboe_vix.vix_open]), 'VixOpen')

    schedule_function(
        rebalance, 
        date_rules.every_day(),
        time_rules.market_open(minutes=1)
    )
    

    
def before_trading_start(context,data):
    context.output = pipeline_output('my_pipeline')
    context.vix = context.output["VixOpen"].iloc[0] 


class GetVIX(CustomFactor):
    window_length = 1
    def compute(self, today, assets, out, vix):
        out[:] = vix[-1]
        
        
def rebalance(context, data):
    
    context.xiv_current = data.current(context.XIV, 'price') 
    price_history = data.history(context.XIV, "price", 20, "1d") 
    context.xiv_mean = price_history.mean()
    
    
    if(context.portfolio.portfolio_value>context.max_value):
        context.PIGGY = context.max_value*context.PIGGY_RATIO
        context.max_value = context.portfolio.portfolio_value
        
        
    tradeable = context.portfolio.portfolio_value-context.CASH-context.PIGGY
    
    if data.can_trade(context.XIV):
        
        
        if(context.vix>25): #if vix too high, bail out!
            order_target_value(context.UVXY, 0)
            order_target_value(context.XIV, 0)
            order_target_value(context.BND,context.PIGGY)
            if(context.holding is not "BAILOUT"):
                    context.holding = "BAILOUT"
                    print context.holding
        else:
            if (context.vix >= 19.8): ##ORIG 19.8 
                order_target_value(context.UVXY, 0)
                order_target_value(context.XIV, tradeable) #Bearish
                order_target_value(context.BND,context.PIGGY) #Bonds
                if(context.holding is not "XIV"):
                    context.holding = "XIV"
                    print context.holding
           
            elif ((context.vix <= 12.2 and context.xiv_current <= context.xiv_mean+2)):
                order_target_value(context.XIV, 0)
                order_target_value(context.UVXY, tradeable) #2x Bullish
                order_target_value(context.BND,context.PIGGY) #Bonds
                if(context.holding is not "UVXY"):
                    context.holding = "UVXY"
                    print context.holding

    track_orders(context,data)
    
def record_orders(context,data):
    pass
    
def track_orders(context, data):
    #record leverage
    #record(Leverage=context.account.leverage)
   
    #record portfolio values
    
    record(value = context.portfolio.portfolio_value)
    record(bnd = context.portfolio.positions[ context.BND].amount * data.current( context.BND, 'price') ) #bond value
    record(cash = context.portfolio.cash)
    record(xiv = context.portfolio.positions[ context.XIV].amount * data.current( context.XIV, 'price') ) #xiv value
    record(uvxy = context.portfolio.positions[ context.UVXY].amount * data.current( context.UVXY, 'price') ) #uvxy
    
    
    #record vix
    #record(vix = context.vix)
    #record(low = 12.2)
    #record(high = 19.8)
    #record(bailout = 25)
    #record(xiv = context.xiv_current)
    #record(xiv_mean = context.xiv_mean+2)
