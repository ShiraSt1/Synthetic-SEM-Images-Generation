import torch
import torch.nn as nn

class UNetBlock(nn.Module):
    def __init__(self, in_ch, out_ch, down=True, use_dropout=False):
        super().__init__()
        if down:
            self.net = nn.Sequential(
                nn.Conv2d(in_ch, out_ch, 4, 2, 1, bias=False),
                nn.BatchNorm2d(out_ch),
                nn.LeakyReLU(0.2, inplace=True),
            )
        else:
            seq = [
                nn.ConvTranspose2d(in_ch, out_ch, 4, 2, 1, bias=False),
                nn.BatchNorm2d(out_ch),
                nn.ReLU(inplace=True),
            ]
            if use_dropout: seq.append(nn.Dropout(0.5))
            self.net = nn.Sequential(*seq)

    def forward(self, x):
        return self.net(x)

class GeneratorUNet(nn.Module):
    def __init__(self, in_ch=1, out_ch=3, base=64):
        super().__init__()
        self.d1 = nn.Sequential(nn.Conv2d(in_ch, base, 4, 2, 1), nn.LeakyReLU(0.2, inplace=True))
        self.d2 = UNetBlock(base, base*2, down=True)
        self.d3 = UNetBlock(base*2, base*4, down=True)
        self.d4 = UNetBlock(base*4, base*8, down=True)
        self.d5 = UNetBlock(base*8, base*8, down=True)
        self.d6 = UNetBlock(base*8, base*8, down=True)
        self.d7 = UNetBlock(base*8, base*8, down=True)
        self.d8 = nn.Sequential(nn.Conv2d(base*8, base*8, 4, 2, 1), nn.ReLU(inplace=True))

        self.u1 = UNetBlock(base*8, base*8, down=False, use_dropout=True)
        self.u2 = UNetBlock(base*16, base*8, down=False, use_dropout=True)
        self.u3 = UNetBlock(base*16, base*8, down=False, use_dropout=True)
        self.u4 = UNetBlock(base*16, base*8, down=False)
        self.u5 = UNetBlock(base*16, base*4, down=False)
        self.u6 = UNetBlock(base*8, base*2, down=False)
        self.u7 = UNetBlock(base*4, base, down=False)
        self.u8 = nn.Sequential(nn.ConvTranspose2d(base*2, out_ch, 4, 2, 1), nn.Tanh())

    def forward(self, x):
        d1 = self.d1(x); d2 = self.d2(d1); d3 = self.d3(d2); d4 = self.d4(d3)
        d5 = self.d5(d4); d6 = self.d6(d5); d7 = self.d7(d6); d8 = self.d8(d7)
        u1 = self.u1(d8)
        u2 = self.u2(torch.cat([u1, d7], 1))
        u3 = self.u3(torch.cat([u2, d6], 1))
        u4 = self.u4(torch.cat([u3, d5], 1))
        u5 = self.u5(torch.cat([u4, d4], 1))
        u6 = self.u6(torch.cat([u5, d3], 1))
        u7 = self.u7(torch.cat([u6, d2], 1))
        out = self.u8(torch.cat([u7, d1], 1))
        return out
