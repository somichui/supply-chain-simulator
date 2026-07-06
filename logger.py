import logging

def setup_logger(name="SupplyChainSim"):
    """
    Sets up a lightweight logging module for the simulation.
    Allows us to track events (INFO) and issues like stockouts (WARNING/ERROR).
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Prevent adding multiple handlers if setup is called multiple times
    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter to include the sim time if we want to pass it, but standard time for now
        formatter = logging.Formatter('%(levelname)s: %(name)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
    return logger

# Default logger instance
sim_logger = setup_logger()
