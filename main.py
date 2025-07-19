import logging
import logging.handlers
import os
import smtplib
from email.message import EmailMessage
import ssl
import smtplib
from dotenv import load_dotenv

load_dotenv()


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_file_handler = logging.handlers.RotatingFileHandler(
    "status.log",
    maxBytes=1024 * 1024,
    backupCount=1,
    encoding="utf8",
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger_file_handler.setFormatter(formatter)
logger.addHandler(logger_file_handler)


def KEMF_LED_Alert():
        from obspy import UTCDateTime as UTC
        from obspy.clients.fdsn import Client

        from scipy.signal import welch
        import numpy as np

        client = Client("IRIS")

        starttime = UTC.now()-3600
        #starttime = UTC('2025-05-24 09:00') # Time of bad data
        st = client.get_waveforms(network='NV', station='KEMF', location='', channel='MHZ', starttime=starttime, endtime=starttime+3600)
        tr = st.merge().detrend()[0]

        NFFT = 256 # 256 is the best value!

        freq, psd = welch(tr.data, fs=round(tr.stats['sampling_rate']), nfft=NFFT)

        # MHZ - Average PSD for bad data
        psd_bad = np.array(
        [8.21113590e+01, 7.64969012e+02, 5.74082692e+02, 4.76320733e+02,
        5.42127616e+02, 6.23902290e+02, 7.44583439e+02, 8.35829159e+02,
        9.38318975e+02, 1.06568618e+03, 1.18732493e+03, 1.36490152e+03,
        1.55279143e+03, 1.61158726e+03, 1.66825645e+03, 1.78112192e+03,
        1.91596801e+03, 2.04104693e+03, 2.05953928e+03, 2.14707206e+03,
        2.18802546e+03, 2.18215900e+03, 2.20858020e+03, 2.26914300e+03,
        2.35432588e+03, 2.34923534e+03, 2.23958282e+03, 2.18368908e+03,
        2.13844578e+03, 2.11676609e+03, 2.09774894e+03, 3.05859502e+03,
        6.08839198e+03, 3.01336044e+03, 1.98751099e+03, 1.92470985e+03,
        1.83018845e+03, 1.73023754e+03, 1.71027465e+03, 1.63163109e+03,
        1.57195295e+03, 1.50708693e+03, 1.48554549e+03, 1.42918610e+03,
        1.37588251e+03, 1.36002278e+03, 1.28897581e+03, 1.24790765e+03,
        1.18228906e+03, 1.11190198e+03, 1.07673080e+03, 1.05443306e+03,
        9.94836946e+02, 9.45508888e+02, 9.19439594e+02, 8.71127230e+02,
        8.27481009e+02, 8.10596368e+02, 7.97270236e+02, 7.42166708e+02,
        7.11896776e+02, 6.92800931e+02, 6.54631732e+02, 1.10098760e+03,
        2.52768321e+03, 1.07514443e+03, 5.49736979e+02, 5.26991196e+02,
        5.08000531e+02, 4.91707963e+02, 4.95323332e+02, 4.76696685e+02,
        4.36925927e+02, 4.37852220e+02, 4.25593246e+02, 4.13385385e+02,
        5.34680567e+02, 5.69188433e+03, 6.62844924e+03, 6.67632882e+02,
        3.46131514e+02, 3.29555358e+02, 3.03712940e+02, 2.95057391e+02,
        2.88776290e+02, 2.82188785e+02, 2.72392436e+02, 2.58543380e+02,
        2.48908264e+02, 2.49082265e+02, 2.46272259e+02, 2.26661479e+02,
        2.20722514e+02, 2.11004752e+02, 2.08779434e+02, 5.16614459e+02,
        1.44444728e+03, 5.05051982e+02, 1.86070277e+02, 1.78022872e+02,
        1.72684429e+02, 1.66958296e+02, 1.75377829e+02, 1.70139090e+02,
        1.56339902e+02, 1.53968834e+02, 1.48233600e+02, 1.45031681e+02,
        1.41434629e+02, 1.37761334e+02, 1.34624815e+02, 1.24933387e+02,
        1.12760215e+02, 9.31404739e+01, 7.01049299e+01, 4.84082308e+01,
        2.79010169e+01, 1.36346450e+01, 5.69403686e+00, 1.97153675e+00,
        5.72378124e-01, 1.42946056e-01, 4.15942496e-02, 2.36761178e-02,
        2.11318400e-02, 2.08423453e-02, 2.08108404e-02, 2.05714655e-02,
        1.00767719e-02])

        cut_off_freq = 1.3 # 20
        quality_metric = np.mean((psd-psd_bad)[freq <= cut_off_freq])


        if quality_metric <= 500:
        # setup email

            sender_email = os.getenv("SENDER")
            receiver_email = os.getenv("UVIC_EMAIL")
            sender_password = os.getenv("UVIC_PASSWD") # Use environment variables or secure methods for production
            subject = "Check email for KEMF SPS"
            body = f"Do something!!! KEMF LED is probably ON, because quality metric ({quality_metric}) is below 500."
            em = EmailMessage()
            em['From'] = sender_email
            em['To'] = receiver_email
            em['subject'] = subject

            em.set_content(body)
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context = context) as smtp:
                        smtp.login(sender_email,sender_password)
                        smtp.sendmail(sender_email,receiver_email,em.as_string())
            return(f"Do something!!! KEMF LED is probably ON, because quality metric ({quality_metric}) is below 500.")

        else:
            print(f"KEMF is probably OK, because quality metric ({quality_metric}) is (hopefully way) above 500.")
       
            return(f"KEMF is probably OK, because quality metric ({quality_metric}) is (hopefully way) above 500.")
        
try:
        
        SOME_SECRET = KEMF_LED_Alert()

except:
        SOME_SECRET = "Script not running!"
        #logger.info("Token not available!")
        #raise


if __name__ == "__main__":

    logger.info(f"{SOME_SECRET}")


    #r = requests.get('https://weather.talkpython.fm/api/weather/?city=Berlin&country=DE')
    #if r.status_code == 200:
    #   data = r.json()
    #    temperature = data["forecast"]["temp"]
    #    logger.info(f'Weather in Berlin: {temperature}')
