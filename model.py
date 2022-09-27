# Simulation model for Multilayer Soil Water Balance

TIME_STEP = 1


class SoilLayer:

    def __init__(self, FC, WP, teta, n=1.8, L=0.5, sat=0.35, depth=100, uptake=0, observation=False):
        self.FC = FC  # Field Capacity (%)
        self.WP = WP  # Wilting Point (%)
        self.s = teta * depth  # initial moisture (mm)
        self.teta = teta  # initial moisture (%)
        self.n = n  # Soil parameter in Van-Genuchten K-Teta equation (n>1)
        self.L = L  # Soil parameter in Van-Genuchten K-Teta equation (L~0.5 -2<L<8)
        self.sat = sat  # soil saturation (mm)
        self.depth = depth
        self.uptake = uptake  # ground water uptake (mm/t)
        self.observation = observation

    #         if teta>sat:
    #             print('Error: initial moisture is higher than saturation!')

    def updateS(self, newS, unit='mm'):
        if unit != 'mm' and unit != '%':
            print('Error: Wrong unit, choose "mm" or "%" instead')

        if unit == 'mm':
            self.s = newS
        elif unit == '%':
            self.s = newS * self.depth

    def updateDepth(self, newDepth):
        self.depth = newDepth

    def reset2FC(self):
        self.s = self.FC * self.depth

    def reset2WP(self):
        self.s = self.WP * self.depth

    def setSat(self, newSat):
        self.sat = newSat * self.depth


# Building anonymos function for various root depths
def rootShapeFunction(da, c, dmax):
    return lambda rootDepth: 1 / (1 + (rootDepth / da) ** (c)) + (
                1 - 1 / (1 + (dmax / da) ** (c))) * rootDepth / dmax  # non-linear shape function
    # return lambda z1,z2:2/rootDepth*(z2-z1)-1/rootDepth**2*(z2**2-z1**2) # Integral of a linear shape function


def cropStress(soilLayer, ro=0.5):
    TAW = soilLayer.FC - soilLayer.WP  # Total available water in percentage
    MAD = TAW * ro  # Management available water in percentage
    teta = soilLayer.s / soilLayer.depth
    if teta > MAD + soilLayer.WP:
        Ks = 1
    elif teta < soilLayer.WP:
        Ks = 0
    else:
        Ks = (teta - soilLayer.WP) / MAD

    return Ks


def layerDescritization(mainLayers, bucketDepth):
    nLayers = len(mainLayers)  # number of layers

    allLayers = []  # initialising all layers list

    bucketCount = -1
    for layer in mainLayers:
        nBuckets = layer.depth / bucketDepth
        for b in range(int(nBuckets)):
            newLayer = SoilLayer(FC=layer.FC, WP=layer.WP, teta=layer.teta, n=layer.n, L=layer.L, depth=bucketDepth,
                                 uptake=layer.uptake, sat=layer.sat)
            allLayers.append(newLayer)
    return allLayers


def hydraulicConductivity(layer, t=TIME_STEP):  # t= time step (hr)
    if layer.s / layer.depth >= layer.sat:
        Se = 1
    else:
        Se = (layer.s / layer.depth - layer.WP) / (layer.sat - layer.WP)
    hc = layer.sat * Se ** layer.L * (
                1 - (1 - Se ** (layer.n / (layer.n - 1))) ** (1 - 1 / layer.n)) ** 2 * 100 / 24 * t
    return hc


def checkLayerDepth(layers, bucketDepth):
    for i, layer in enumerate(layers):
        if layer.depth % bucketDepth != 0:
            print('Error: Layer {} is not dividable by the bucket size'.format(i))
