#!/usr/bin/python
# -*- coding: utf-8 -*-

import random, sys
import interface
import traceback

class KnightBot(interface.Bot):
    """Bot que juega siguiendo las reglas del buen caballero."""
    NAME = "KnightBot"
            
    def nextObjective(self,lighthouses,cx, cy):
        try:     
            #TODO poner que no sea elegido a lo random si no que se elija por cercania y sin cruzar lineas
            if self.selectedLighthouse == (-1,-1):
                lighthousesPositions = list(lighthouses)
                for lighthouseAlreadyAttacked in self.listOfLighthousesCaptured:                   
                    self.log(str(lighthouseAlreadyAttacked))
                    lighthousesPositions.remove(lighthouseAlreadyAttacked)
                if len(self.listOfLighthousesCaptured) == 3:
                    self.log("Atacando el primero para cerrar el circulo")
                    self.log(str(self.listOfLighthousesCaptured[0]))
                    self.selectedLighthouse = self.listOfLighthousesCaptured[0]
                else:
                    self.selectedLighthouse = random.choice(lighthousesPositions)
                # TODO cambiarlo para que no sea solo por X si no que calcule bien los pasos que necesita para llegar
                self.numberOfTurnsToReach = abs(cx - self.selectedLighthouse[0]) + 10
                self.log(str(self.selectedLighthouse))
            posObjX, posObjY = self.selectedLighthouse
            deltaX = 0
            deltaY = 0
            if cx > posObjX:
                deltaX = -1 
            elif cx < posObjX:
                deltaX = 1            
            if cy > posObjY:
                deltaY = -1 
            elif cy < posObjY:
                deltaY = 1       
            maxIter = 0
            while self.map[cx+deltaX][cy+deltaY] == 0 and maxIter < 5:
                self.log("Resulta que estoy intentando moverme a un campo que no se puede pisar, recalculando ruta")
                if not self.map[cx+deltaX][cy] == 0:
                    deltaY = 0
                elif not self.map[cx][cy+deltaY] == 0:            
                    deltaX = 0
                elif not self.map[cx-deltaX][cy] == 0:
                	deltaX = -deltaX   
                elif not self.map[cx][cy+deltaY] == 0:
                	deltaY = -deltaY        
            maxIter += 1      
            move = (deltaX,deltaY) 
            return move
        except:
            traceback.print_exc()
            self.listOfLighthousesCaptured = []
            self.log("Erroraso, revisar porque ha petado.")
            return(0,0)
    
    def __init__(self, init_state):
        self.selectedLighthouse = (-1,-1)
        self.listOfLighthousesCaptured = []
        self.numberOfTurnsToReach = -1
        self.numberOfTurnsExecuted = -1
        super().__init__(init_state)
        
    def play(self, state):
        """Jugar: llamado cada turno.
        Debe devolver una acción (jugada)."""
        cx, cy = state["position"]
        lighthouses = dict((tuple(lh["position"]), lh)
                            for lh in state["lighthouses"])
        # TODO hacer chequeo de los lighthouses que he atacado para ver si el owner sigo siendo yo, si no lo soy los quito de la lista de capturados para que sean objetivo de nuevo
        # Para evitar bloqueos por caminos no calculables de momento
        self.numberOfTurnsExecuted += 1 
        if self.numberOfTurnsExecuted > self.numberOfTurnsToReach:
            self.numberOfTurnsToReach = -1
            self.numberOfTurnsExecuted = -1
            self.selectedLighthouse = (-1,-1)
        
        # Si estamos en un faro...
        if (cx, cy) in lighthouses:
            isLighthouseMine = lighthouses[(cx, cy)]["owner"] == self.player_num
            if isLighthouseMine:
                possible_connections = []
                for dest in lighthouses:
                    # No conectar con sigo mismo
                    # No conectar si no tenemos la clave
                    # No conectar si ya existe la conexión
                    # No conectar si no controlamos el destino
                    # Nota: no comprobamos si la conexión se cruza.
                    if (dest != (cx, cy) and
                        lighthouses[dest]["have_key"] and
                        [cx, cy] not in lighthouses[dest]["connections"] and
                        lighthouses[dest]["owner"] == self.player_num):
                        possible_connections.append(dest)

                if possible_connections:
                
                    for conn in possible_connections:
                        self.log("conn "+ str(conn))
                    # TODO algo extraño hace con esto, creo que es porque como para ir de un faro objetivo a otro piso otros faros cojo la key de ese faro y la lio gorda, deberia esquivar los faros
                    if len(self.listOfLighthousesCaptured) == 3:
                        self.listOfLighthousesCaptured = []
                    return self.connect(random.choice(possible_connections))

            elif not isLighthouseMine:
                #self.log("Energia disponible "+str(state["energy"] ))
                # Lanzamos toda la energia de la fuerza de mil soles para capturar este objetivo
                energy = state["energy"]
                self.listOfLighthousesCaptured.append(self.selectedLighthouse)
                self.selectedLighthouse = (-1,-1)
                return self.attack(energy)

        # Determinar movimientos válidos
        move = self.nextObjective(lighthouses,cx,cy)  
        return self.move(*move)
        
    def success(self):
        """Éxito! La jugada ha salido fetén."""
        pass

    def error(self, message, last_move):
        """Error: Liadita gorda. Recalcular estrategia"""
	# Reset de variables
        self.selectedLighthouse = (-1,-1)
        self.listOfLighthousesCaptured = []
        self.log("Recibido error: %s", message)
        self.log("Jugada previa: %r", last_move)

if __name__ == "__main__":
    iface = interface.Interface(KnightBot)
    iface.run()
