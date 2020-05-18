#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Dependencies
import logging
from emoji import emojize
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import ChatAction
import mysql.connector
import array as arr
from ConfigParser import ConfigParser
import os.path

# Habilitem el logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

# Per obtenir els paràmetres del fitxer de configuració
config = ConfigParser()
path = os.path.dirname(os.path.abspath(__file__))
config.read(path + "/config.ini")

# Constants
TOKEN = config.get("TELEGRAM","TOKEN")
URL = config.get("TELEGRAM","URL")
PORT = config.getint("TELEGRAM","PORT")
CERT = config.get("TELEGRAM","CERT")
KEY = config.get("TELEGRAM","KEY")

BD_HOST = config.get("DATABASE","BD_HOST")
BD_USER = config.get("DATABASE","BD_USER")
BD_PASS = config.get("DATABASE","BD_PASS")
BD_NAME = config.get("DATABASE","BD_NAME")

ICONA_OK = emojize(":thumbs_up:", use_aliases=True)
INCONA_CARA_PREOCUPAT = emojize(":confused_face:", use_aliases=True)


def getHelpText():
    """Genera el missatge d'ajuda."""
    
    str_ajuda = ""
    str_ajuda += "/start inicia el bot. \n"
    str_ajuda += "/help si necessites ajuda. \n"
    str_ajuda += "/question si vols que et formuli preguntes. \n"
    str_ajuda += "/topic per escollir una temàtica de preguntes. \n"
    str_ajuda += "/stats et mostraré les teves estadístiques. \n"
    str_ajuda += "/reset inicialitza les teves estadístiques. \n\n"
    str_ajuda += "En cas de detectar una incongruència en una pregunta, pots comunicar-ho aportant l'identificador de la pregunta. Cada pregunta s'identifica amb la seva capçalera on apareix la seva temàtica seguit d'un codi entre coixinets.\nPer exemple: 'PRESSUPOST - #17#' . \n\n"
    str_ajuda += "Pots contribuir en ampliar i millorar les preguntes d'aquest projecte des de la web https://intersarsi.duckdns.org:8080/opodipbot/"
    
    return str_ajuda

def start(bot, update):
    """Funció que s'executa quan l'usuari envia la comanda /start."""
    
    #Simulem que el bot està escribint alguna cosa
    bot.send_chat_action(chat_id=update.message.chat.id, action=ChatAction.TYPING)
    
    #Recollim informació de l'usuari
    idUsuari = update.message.from_user.id
    nomUsuari = str(update.message.from_user.first_name)
    
    logger.info("L'usuari %s ha executat la comanda /start", idUsuari)
    
    #Creem connexió a la base de dades
    mydb = mysql.connector.connect(
        host=BD_HOST,
        user=BD_USER,
        passwd=BD_PASS,
        database=BD_NAME
    )
    
    mycursor = mydb.cursor()
    
    #Comprovem si l'usuari ja existeix a la base de dades
    myquery = "SELECT COUNT(idUsuari) FROM usuari WHERE idUsuari = %s"
    myparams = (idUsuari, )
    mycursor.execute(myquery, myparams)
    myresult = mycursor.fetchall()
    
    if myresult[0][0] > 0 :
        #Actualitzem la informació de l'usuari
        myquery = "UPDATE usuari SET nom = %s, idCategoriaActiva = %s WHERE idUsuari = %s"
        myparams = (nomUsuari, 0, idUsuari)
    else:
        #Donem d'alta el nou usuari
        myquery = "INSERT INTO usuari (idUsuari, nom, idCategoriaActiva, dataAlta, idHistorialStats, bloquejat) VALUES (%s, %s, %s, now(), %s, %s)"
        myparams = (idUsuari, nomUsuari, 0, 0, 1)
    
    mycursor.execute(myquery, myparams)
    
    mydb.commit()
    
    mycursor.close()
    mydb.close()
    
    str_benvinguda = "Hola " + nomUsuari + "! \n\nEstic content de veure't per aquí!\nComencem? \n\n"
    str_benvinguda += getHelpText()
    update.message.reply_text(str_benvinguda)


def help(bot, update):
    """Send a message when the command /help is issued."""
    
    #Simulem que el bot està escribint alguna cosa
    bot.send_chat_action(chat_id=update.message.chat.id, action=ChatAction.TYPING)
    
    #Recollim informació de l'usuari
    idUsuari = update.message.from_user.id
    nomUsuari = str(update.message.from_user.first_name)
    
    logger.info("L'usuari %s ha executat la comanda /help", idUsuari)
    
    update.message.reply_text(getHelpText())
    
def topic(bot, update):
    
    #Simulem que el bot està escribint alguna cosa
    bot.send_chat_action(chat_id=update.message.chat.id, action=ChatAction.TYPING)
    
    #Recollim informació de l'usuari
    idUsuari = update.message.from_user.id
    nomUsuari = str(update.message.from_user.first_name)
    
    logger.info("L'usuari %s ha executat la comanda /topic", idUsuari)
    
    #Obrim la connexió amb la base de dades
    mydb = mysql.connector.connect(
        host=BD_HOST,
        user=BD_USER,
        passwd=BD_PASS,
        database=BD_NAME
    )
    
    mycursor = mydb.cursor()
    
    #Obtenim les categories
    myquery = "SELECT idCategoria, nom FROM categoria ORDER BY nom"
    myparams = ()
    
    mycursor.execute(myquery, myparams)
    
    myresult = mycursor.fetchall()
    
    keyboard = []
    keyboardrow = []
    
    for resposta in myresult:
        
        str_id = str(resposta[0])
        key = InlineKeyboardButton(resposta[1].encode('utf-8'), callback_data=str_id)
        keyboardrow = []
        keyboardrow.append(key)
        keyboard.append(keyboardrow)
    
    #Tanquem la connexió amb la base de dades
    mycursor.close()
    mydb.close()
    
    #Indiquem en el teclat les tecles que tindrà
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Preguntem a l'usuari quina categoria vol escollir (cada tecla del teclat serà una temàtica a escollir)
    update.message.reply_text("Escull una temàtica: ", reply_markup=reply_markup)
    
def topic_answer(bot, update):
    
    #Simulem que el bot està escribint alguna cosa
    #bot.send_chat_action(chat_id=update.message.chat.id, action=ChatAction.TYPING)
    
    query = update.callback_query
    
    #Recollim informació de l'usuari
    #idUsuari = update.message.from_user.id
    idUsuari = query.from_user.id
    
    logger.info("L'usuari %s ens ha indicat la idCategoria = %s", idUsuari, query.data)
    
    #Obrim la connexió amb la base de dades
    mydb = mysql.connector.connect(
        host=BD_HOST,
        user=BD_USER,
        passwd=BD_PASS,
        database=BD_NAME
    )
    
    mycursor = mydb.cursor()
    
    #Obtenim informació de la categoria seleccionada per l'usuari
    myquery = "SELECT p.idCategoria, c.nom, count(p.idCategoria) "
    myquery += "FROM pregunta p "
    myquery += "LEFT JOIN categoria c ON p.idCategoria = c.idCategoria "
    myquery += "WHERE p.idCategoria = %s "
    myquery += "GROUP BY p.idCategoria "
    
    myparams = (query.data, )
    mycursor.execute(myquery, myparams)
    myresult = mycursor.fetchone()
    
    if myresult :
        #La consulta a la base de dades ha retornat dades, per tant tenim preguntes per aquesta categoria
        idCategoria = myresult[0]
        nomCategoria = myresult[1].encode('utf-8').lower()
        numPreguntesCategoria = myresult[2]
    else :
        #La consulta a la base de dades no ha retornat cap fila, per tant no tenim preguntes per aquesta categoria
        idCategoria = int(query.data)
        nomCategoria = ""
        numPreguntesCategoria = 0
    
    actualitzarCategoria = False;
    
    if idCategoria == 0 :
        str_resposta = "D'acord!\nA partir d'ara et faré preguntes variades sobre les diferents temàtiques.\n\n"
        str_resposta += "Digue'm /question per plantejar-te preguntes de nou o /topic per modificar de temàtica."
        actualitzarCategoria = True;
    else :
        if numPreguntesCategoria == 0 :
            str_resposta = "No t'he modificat la temàtica, ja que encara no tinc preguntes per plantejar-te sobre aquest tema...\n\n"
            str_resposta += "Ajuda'm a aprendre a fer-te noves preguntes. Des de la web https://intersarsi.duckdns.org:8080/opodipbot/\n\n"
            str_resposta += "Digue'm /question per plantejar-te preguntes de nou o /topic per modificar de temàtica."
            actualitzarCategoria = False;
            #topic(bot, update)
        elif numPreguntesCategoria <= 10:
            str_resposta = "D'acord!\nA partir d'ara et faré preguntes sobre " + nomCategoria + ". Tot i que no tinc moltes preguntes per fer-te...\n\n"
            str_resposta += "Ajuda'm a aprendre a fer-te noves preguntes sobre " + nomCategoria + ". Des de la web https://intersarsi.duckdns.org:8080/opodipbot/\n\n"
            str_resposta += "Digue'm /question per plantejar-te preguntes de nou o /topic per modificar de temàtica."
            actualitzarCategoria = True;
        else :
            str_resposta = "D'acord!\nA partir d'ara et faré preguntes sobre " + nomCategoria + ".\n\n"
            str_resposta += "Digue'm /question per plantejar-te preguntes de nou o /topic per modificar de temàtica."
            actualitzarCategoria = True;
    
    if actualitzarCategoria == True :
        #Actualitzem la informació de la categoria de l'usuari
        myquery = "UPDATE usuari SET idCategoriaActiva = %s WHERE idUsuari = %s"
        myparams = (idCategoria, idUsuari)
        mycursor.execute(myquery, myparams)
        mydb.commit()
        logger.info("Li hem actualitzat la categoria a l'usuari %s correctament", idUsuari)
    
    #Tanquem la connexió amb la base de dades
    mycursor.close()
    mydb.close()
    
    bot.edit_message_text(text=str_resposta, chat_id=query.message.chat_id, message_id=query.message.message_id)
    
def stats(bot, update):
    
    #Simulem que el bot està escribint alguna cosa
    bot.send_chat_action(chat_id=update.message.chat.id, action=ChatAction.TYPING)
    
    #Recollim informació de l'usuari
    idUsuari = update.message.from_user.id
    nomUsuari = str(update.message.from_user.first_name)
    
    logger.info("L'usuari %s ha executat la comanda /stats", idUsuari)
    
    #Obrim la connexió amb la base de dades
    mydb = mysql.connector.connect(
        host=BD_HOST,
        user=BD_USER,
        passwd=BD_PASS,
        database=BD_NAME
    )
    
    mycursor = mydb.cursor()
    
    #Obtenim la quantiat de preguntes respostes corresctes i incorrectes
    myquery = "SELECT 'ok', COUNT(encertada) "
    myquery += "FROM historial_respostes "
    myquery += "WHERE idUsuari = %s AND encertada = 1 AND idHistorial > (SELECT idHistorialStats FROM usuari WHERE idUsuari = %s) "
    myquery += "UNION "
    myquery += "SELECT 'ko', COUNT(encertada) "
    myquery += "FROM historial_respostes "
    myquery += "WHERE idUsuari = %s AND encertada = 0 AND idHistorial > (SELECT idHistorialStats FROM usuari WHERE idUsuari = %s) "
    
    myparams = (idUsuari, idUsuari, idUsuari, idUsuari, )
    mycursor.execute(myquery, myparams)
    myresult = mycursor.fetchall()
    
    numEncerts = 0
    numErrors = 0
    
    for resposta in myresult:
        
        if resposta[0] == 'ok':
            numEncerts = resposta[1]
        elif resposta[0] == 'ko' :
            numErrors = resposta[1]
        
    
    #Tanquem connexió amb la base de dades
    mycursor.close()
    mydb.close()
    
    if (numEncerts + numErrors) > 0 :
        resultats = "Les teves estadístiques personals: \n\n"
        resultats += "Has respost un total de " + str(numEncerts + numErrors) + " preguntes.\n"
        resultats += "- Encerts: " + str(numEncerts) + " (" + str((numEncerts * 100) / (numEncerts + numErrors)) + "%)\n"
        resultats += "- Errors: " + str(numErrors) + " (" + str((numErrors * 100) / (numEncerts + numErrors)) + "%)\n\n"
        resultats += "Per inicialitzar les teves estadístiques digue'm /reset."
    else :
        resultats = "Primer respon a algunes preguntes..."
    
    update.message.reply_text(resultats)
    
def reset(bot, update):
    """Funció que inicialitzarà les estadístiques de l'usuari."""
    
    #Simulem que el bot està escribint alguna cosa
    bot.send_chat_action(chat_id=update.message.chat.id, action=ChatAction.TYPING)
    
    #Recollim informació de l'usuari
    idUsuari = update.message.from_user.id
    nomUsuari = str(update.message.from_user.first_name)
    logger.info("L'usuari %s ha executat la comanda /reset", idUsuari)
    
    #Creem connexió a la base de dades
    mydb = mysql.connector.connect(
        host=BD_HOST,
        user=BD_USER,
        passwd=BD_PASS,
        database=BD_NAME
    )
    
    mycursor = mydb.cursor()
    
    myquery = "UPDATE usuari "
    myquery += "SET idHistorialStats = (SELECT IFNULL(MAX(idHistorial),0) FROM historial_respostes WHERE idUsuari = %s) "
    myquery += "WHERE idUsuari = %s "
    myparams = (idUsuari, idUsuari)
    mycursor.execute(myquery, myparams)
    mydb.commit()
    
    #Tanquem connexió amb la base de dades
    mycursor.close()
    mydb.close()
    
    update.message.reply_text("S'han inicialitzat les teves estadístiques.")
    
def error(bot, update):
    """Log Errors caused by Updates."""
    logger.warning("S'ha produït un error. Update: %s Causat per: %s", update, context.error)
    
def question(bot, update):
    """Farà sortir una pregunta amb les diferents opcions en un teclat"""
    
    #Simulem que el bot està escribint alguna cosa
    bot.send_chat_action(chat_id=update.message.chat.id, action=ChatAction.TYPING)
    
    #Recollim informació de l'usuari
    idUsuari = update.message.from_user.id
    nomUsuari = str(update.message.from_user.first_name)
    logger.info("L'usuari %s ha executat la comanda /question", idUsuari)
    
    #Obrim la connexió amb la base de dades
    mydb = mysql.connector.connect(
        host=BD_HOST,
        user=BD_USER,
        passwd=BD_PASS,
        database=BD_NAME
    )
    
    mycursor = mydb.cursor()
    
    #Obtenim de quina categoria hem de seleccionar la pregunta
    myquery = "SELECT idCategoriaActiva, bloquejat FROM usuari WHERE idUsuari = %s "
    myparams = (idUsuari, )
    mycursor.execute(myquery, myparams)
    myresult = mycursor.fetchone()
    idCategoria = myresult[0]
    bloquejat = myresult[1]
    
    #Si l'usuari està bloquejat, no li mostrarem cap pregunta
    if bloquejat == True :
        update.message.reply_text("Ara que ho penso... No estic segur que et conegui...\n\nParla amb qui m'ha desenvolupat perquè m'autoritzi a fer-te preguntes.")
    else :
        
        #Mirem si per la categoria que esta l'usuari, ha respost ja totes les preguntes
        #Si fos així, eliminariem les files de la taula "preguntes_realitzades" que corresponen a l'usuari per la categoria concreta
        if idCategoria > 0 :
            where_categoria = "WHERE idCategoria = %s"
            where_categoria2 = "AND idCategoria = %s"
            myparams = (idCategoria, idUsuari, idCategoria, )
            myparams2 = (idUsuari, idCategoria, )
        else :
            where_categoria = ""
            where_categoria2 = ""
            myparams = (idUsuari, )
            myparams2 = (idUsuari, )

        myquery = ""
        myquery += "SELECT "
        myquery += "(SELECT COUNT(idPregunta) FROM pregunta " + where_categoria + ") AS 'total', "
        myquery += "(SELECT count(idPregunta) FROM preguntes_realitzades WHERE idUsuari = %s " + where_categoria2 + ") AS 'fetes' "
        mycursor.execute(myquery, myparams)
        myresult = mycursor.fetchone()

        if myresult[0] <= myresult[1] :
            #Ja ha respost totes les de la categoria, eliminem les files de totes les que ha respost de la categoria
            myquery = "DELETE FROM preguntes_realitzades WHERE idUsuari = %s " + where_categoria2 + " "
            mycursor.execute(myquery, myparams2)

        #Obtenim el text de la pregunta
        myparams = ()
        myquery = ""
        myquery += "SELECT p.idCategoria, c.nom AS 'categoria', p.idPregunta, p.descripcio "
        myquery += "FROM pregunta p "
        myquery += "LEFT JOIN categoria c ON p.idCategoria = c.idCategoria "
        #myquery += "WHERE idPregunta = %s "
        #myparams = (id_pregunta, )

        if idCategoria > 0 :
            myquery += "WHERE p.idCategoria = %s AND "
            myquery += "idPregunta NOT IN (SELECT idPregunta FROM preguntes_realitzades WHERE idUsuari = %s AND idCategoria = %s) "
            myquery += "ORDER BY RAND() LIMIT 1"
            myparams = (idCategoria, idUsuari, idCategoria, )
            mycursor.execute(myquery, myparams)
        else :
            myquery += "WHERE idPregunta NOT IN (SELECT idPregunta FROM preguntes_realitzades WHERE idUsuari = %s) "
            myquery += "ORDER BY RAND() LIMIT 1"
            myparams = (idUsuari, )
            mycursor.execute(myquery, myparams)


        myresult = mycursor.fetchone()

        str_question = myresult[1].encode('utf-8').upper() + " - #" + str(myresult[2]) + "#\n\n" + myresult[3].encode('utf-8') + "\n\n"
        id_pregunta = myresult[2]
        id_categoria = myresult[0]

        #Ara que sabem la pregunta que mostrarem a l'usuari, ens guardem a la taula preguntes_realitzades la pregunta que hem plantejat a l'usuari
        #Així evitem que es torni a enviar (repetir) aquesta mateixa pregunta a l'usuari abans no les hagi contestat totes les de la mateixa categoria
        myquery = "INSERT INTO preguntes_realitzades (idUsuari, idCategoria, idPregunta) VALUES (%s, %s, %s)"
        myparams = (idUsuari, id_categoria, id_pregunta)
        mycursor.execute(myquery, myparams)
        mydb.commit()

        #Obtenim el text de les possibles respostes
        myquery = "SELECT idPregunta, idResposta, descripcio, esCorrecte FROM resposta WHERE idPregunta = %s ORDER BY rand()"
        myparams = (id_pregunta, )

        mycursor.execute(myquery, myparams)

        myresult = mycursor.fetchall()

        keyboard = []
        keyboardrow = []
        lletres = ["A","B","C","D"]
        idRespostaCorrecta = 0
        codiRespostaCorrecta = ''
        i = 0

        #Recorrem totes les respostes possibles
        for resposta in myresult:

            #Generem el text d'una de les respostes
            str_question += lletres[i] + ") " + resposta[2].encode('utf-8') + "\n\n"

            #Creem una tecla del teclat de respostes
            key = KeyboardButton(lletres[i])

            ##Per a cada fila del teclat de respostes només tindrem màxim dos botons, sinó creem nova fila de botons (ocupa més espai de pantalla a l'usuari)
            #if len(keyboardrow) == 2 :
            #    keyboard.append(keyboardrow)
            #    keyboardrow = []
            #    keyboardrow.append(key)
            #else :
            #    keyboardrow.append(key)

            #Creem una sola fila on hi apareixeran tots els botons (ocupa menys espai de pantalla a l'usuari)
            keyboardrow.append(key)

            #Ens guardem la ID de la resposta que és la correcta
            if resposta[3] == 1:
                idRespostaCorrecta = resposta[1]
                codiRespostaCorrecta = lletres[i]

            i +=1

        #Ens guardarem a la fila de la base de dades de l'usuari la resposta correcta a la pregunta plantejada a l'usuari
        #Per poder validar la resposta que ens donarà l'usuari
        myquery = "UPDATE usuari SET idPreguntaPendent = %s, idRespostaPendent = %s, codiRespostaPendent = %s WHERE idUsuari = %s"
        myparams = (id_pregunta, idRespostaCorrecta, codiRespostaCorrecta, idUsuari)
        mycursor.execute(myquery, myparams)
        mydb.commit()

        #Tanquem la connexió amb la base de dades
        mycursor.close()
        mydb.close()

        #Afegim els botons de l'última fila creats en el teclat de respostes
        keyboard.append(keyboardrow)

        # Indiquem en el teclat les tecles que tindrà
        reply_markup = ReplyKeyboardMarkup(keyboard, True, False)

        # Enviem pregunta amb les possibles respostes (cada tecla del teclat serà una resposta possible)
        update.message.reply_text(str_question, reply_markup=reply_markup)
    
    
def answer(bot, update):
    """Funció que analitzarà la resposta, segons l'opció del teclat que l'usuari hagi clicat"""
    
    #Recollim informació de l'usuari
    idUsuari = update.message.from_user.id
    logger.info("L'usuari %s ha respost una pregunta", idUsuari)
    
    #Simulem que el bot està escribint alguna cosa
    bot.send_chat_action(chat_id=update.message.chat.id, action=ChatAction.TYPING)
    
    #Passem a majúscules i treiem els espais en blanc de la resposta que ens ha enviat l'usuari
    resposta = update.message.text.encode('utf-8').upper().strip()
    
    #Comprovem que sigui una resposta vàlida (una lletra: A, B, C o D)
    if resposta == 'A'or resposta == 'B' or resposta == 'C' or resposta == 'D':
        
        logger.info("Resposta rebuda amb format correcte de l'usuari %s ", idUsuari)
        
        #Obrim la connexió amb la base de dades
        mydb = mysql.connector.connect(
            host=BD_HOST,
            user=BD_USER,
            passwd=BD_PASS,
            database=BD_NAME
        )
        
        mycursor = mydb.cursor()
        
        #Contrastem que la resposta donada per l'usuari és la resposta correcta
        myquery = "SELECT idPreguntaPendent, idRespostaPendent, codiRespostaPendent FROM usuari WHERE idUsuari = %s"
        myparams = (idUsuari, )

        mycursor.execute(myquery, myparams)

        myresult = mycursor.fetchone()
        
        idPregunta = myresult[0]
        respostaEsperada = myresult[2].encode('utf-8')
        esCorrecte = False
        
        if respostaEsperada == resposta :
            esCorrecte = True
        else :
            esCorrecte = False
            
        
        #Guardem a la taula de l'historial de la base de dades la resposta que ha donat l'usuari
        myquery = "INSERT INTO historial_respostes (idUsuari, idPregunta, encertada, dataHora) VALUES (%s, %s, %s, now())"
        myparams = (idUsuari, idPregunta, esCorrecte)
        mycursor.execute(myquery, myparams)
        mydb.commit()
        
        #Tanquem la connexió amb la base de dades
        mycursor.close()
        mydb.close()
        
        
        #Comuniquem a l'usuari la correcció de la pregunta (si l'ha encertat o no)
        if esCorrecte == True :
            update.message.reply_text(ICONA_OK)
            update.message.reply_text("Correcte! ")
        else :
            update.message.reply_text(INCONA_CARA_PREOCUPAT)
            update.message.reply_text("No és correcte... Era la " + respostaEsperada)
        
        #Un cop resposta la pregunta actual, formulem una nova pregunta a l'usuari
        question(bot, update)
        
    else:
        logger.info("Resposta rebuda amb format incorrecte de l'usuari %s ", idUsuari)
        update.message.reply_text("No t'entenc...")
        
    

# Metode principal del programa
def main():

    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN)

    # Creem la URL completa del nostre WebHook
    urlWebHook = URL + ":" + str(PORT) + "/"  + TOKEN

    # Iniciem el "mini" servidor web ofereix la llibreria per aixecar un servei web

    logger.info("PORT: %s ", PORT)
    logger.info("KEY: %s ", KEY)
    logger.info("CERT: %s ", CERT)
    logger.info("URL WEBHOOK: %s ", urlWebHook)

    updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=TOKEN,
                      key=KEY,
                      cert=CERT,
                      clean="True",
                      webhook_url=urlWebHook)
    
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("topic", topic))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("reset", reset))

    # Relacionem l'ordre que ens arribi amb la funció que s'ha de desencadenar quan es recepciona un event de tipus pregunta
    question_handler = CommandHandler('question', question)
    dp.add_handler(question_handler)

    # Relacionem l'ordre que ens arribi amb la funció que s'ha de desencadenar quan es recepciona un event de tipus resposta
    dp.add_handler(MessageHandler(Filters.text, answer))
    
    dp.add_handler(CallbackQueryHandler(topic_answer))
    
    # log all errors
    dp.add_error_handler(error)

    logger.info("EL BOT ESTÀ PREPARAT I LLEST!")
    
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
    
    
# Punt de partida de l'inici d'execusio del programa
if __name__ == '__main__':
    main()
