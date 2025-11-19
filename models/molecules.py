from models.base import TimeStampedModel
from sqlalchemy import Column, Integer, ForeignKey, String, Text
from sqlalchemy.orm import Relationship
from sqlalchemy.sql.sqltypes import Enum as SAEnum
from user.allowed_values import Chromophores, Doublets, Linker, Radicals


class Molecule(TimeStampedModel):
    __tablename__ = "molecules"

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String(512), nullable=False, unique=True)
    molecular_formula = Column(String(124), nullable=False)
    structural_formula = Column(Text, unique=True, nullable=False)
    smiles = Column(Text, unique=True, nullable=False)

    measurements = Relationship("Measurement", back_populates="molecule",
                                    passive_deletes=True)

    group = Column(String(20), nullable=False)
    __mapper_args__ = {
        "polymorphic_on": group,
        "polymorphic_identity": "base",
        }

    def __repr__(self):

        return f"({self.__class__.__name__}: {self.name}, {self.id})"


class Single(Molecule):
    __tablename__ = "single"

    id = Column(Integer, ForeignKey("molecules.id", ondelete="CASCADE"),
                primary_key=True)

    additional_info = Column(Text)

    __mapper_args__ = {"polymorphic_identity": "single",}


class RP(Molecule):
    __tablename__ = "rp"

    id = Column(Integer, ForeignKey("molecules.id", ondelete="CASCADE"),
                primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "rp",}

    radical_1 = Column(SAEnum(Radicals), nullable=False)
    linker = Column(SAEnum(Linker), nullable=False)
    radical_2 = Column(SAEnum(Radicals), nullable=False)


class TDP(Molecule):
    __tablename__ = "tdp"

    id = Column(Integer, ForeignKey("molecules.id", ondelete="CASCADE"),
                primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "tdp",}

    doublet = Column(SAEnum(Doublets), nullable=False)
    linker = Column(SAEnum(Linker), nullable=False)
    chromophore = Column(SAEnum(Chromophores), nullable=False)



class TTP(Molecule):
    __tablename__ = "ttp"

    id = Column(Integer, ForeignKey("molecules.id", ondelete="CASCADE"),
                primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "ttp",}

    triplet_1= Column(SAEnum(Chromophores), nullable=False)
    linker = Column(SAEnum(Linker), nullable=False)
    triplet_2 = Column(SAEnum(Chromophores), nullable=False)
