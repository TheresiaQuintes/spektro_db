from specatalog.models.base import TimeStampedModel
from sqlalchemy import Column, Integer, ForeignKey, String, Text
from sqlalchemy.orm import Relationship
from sqlalchemy.sql.sqltypes import Enum as SAEnum

from specatalog.main import BASE_PATH
import importlib.util
spec = importlib.util.spec_from_file_location("allowed_values", BASE_PATH / "allowed_values.py")
av = importlib.util.module_from_spec(spec)
spec.loader.exec_module(av)


class Molecule(TimeStampedModel):
    """
    Base clase representing a molecule.

    This class represents a chemical molecule, including both basic descriptive
    metadata (name, molecular formula) and a structural representation. It
    serves as the base class for a polymorphic hierarchy of molecule types,
    enabling specialised subclasses to extend the core attributes defined here.

    The ``measurements`` relationship links each molecule to all associated
    spectroscopic measurements, with deletions cascading automatically to
    dependent measurement entries.

    Attributes
    ----------
    id : int
        Primary key of the molecule entry.
    name : str
        Human-readable molecular name. Must be unique.
    molecular_formula : str
        Standard chemical formula such as ``C20H14O``.
    structural_formula : str
        Path to a file with the structural formula (e.g. .cdx and .pdf format).
        The file should be saved at ``/molecules/MOLxy``.
        Must be unique.
    measurements : list[Measurement]
        All spectroscopic measurements associated with this molecule.
    group : str
        Polymorphic discriminator used by SQLAlchemy to select the correct
        molecule subclass upon loading.

    Notes
    -----
    * The tablename is ``molecules``.
    * This class forms the base of a polymorphic SQLAlchemy hierarchy.
    * Subclasses define their own ``polymorphic_identity`` values.
    * The ``measurements`` relationship uses ``passive_deletes=True`` so that
      deleting a molecule cascades to related measurement entries
      automatically.
    * Timestamp fields ``created_at`` and ``updated_at`` are inherited from
      :class:`TimeStampedModel`.

    Examples
    --------
    Creating a molecule:

    >>> from models import Molecule
    >>> mol = Molecule(
    ...     name="Perylene",
    ...     molecular_formula="C20H12",
    ...     structural_formula="/molecule/MOL5",
    ...     group="base",
    ... )
    >>> session.add(mol)
    >>> session.commit()

    Accessing linked measurements:

    >>> mol = session.get(Molecule, 5)
    >>> mol.measurements
    [Measurement(...), TREPR(...), PulseEPR(...)]
    """
    __tablename__ = "molecules"

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String(512), nullable=False, unique=True)
    molecular_formula = Column(String(124), nullable=False)
    structural_formula = Column(Text, unique=True, nullable=False)

    measurements = Relationship("Measurement", back_populates="molecule",
                                    passive_deletes=True)

    group = Column(String(20), nullable=False)
    __mapper_args__ = {
        "polymorphic_on": group,
        "polymorphic_identity": "base",
        }

    def __repr__(self):

        return f"({self.__class__.__name__}: {self.name}, {self.id})"


class SingleMolecule(Molecule):
    """
    Single-molecule entry in the molecular hierarchy.

    This subclass of :class:`Molecule` represents an individual, well-defined
    molecular species without further structural partitioning. While the base
    :class:`Molecule` class already provides universal molecular attributes
    (name, molecular formula, structural representation), this class allows the
    addition of optional, molecule-specific descriptive information.

    The model participates in the polymorphic SQLAlchemy hierarchy using the
    ``"single"`` ``polymorphic_identity``. Any row in ``molecules`` where
    ``group='single'`` will therefore be loaded as a :class:`SingleMolecule`
    instance.

    Attributes
    ----------
    id : int
        Primary key linked to ``molecules.id`` with cascading delete.
    additional_info : str or None
        Optional free-text field containing supplementary information about
        the molecule.

    Notes
    -----
    * The table name is ``single``.
    * Inherits all mandatory molecular attributes from :class:`Molecule`
      (name, molecular_formula, structural_formula, timestamps, relationships).
    * ``id`` maps directly to the base ``molecules`` table through joined-table
      inheritance.
    * ``additional_info`` is optional and may remain empty.
    * All molecules that do not fit to an other class should be from
      :class:`SingleMolecule`.

    Examples
    --------
    Creating a single molecule:

    >>> from models import SingleMolecule
    >>> s = SingleMolecule(
    ...     name="Anthracene",
    ...     molecular_formula="C14H10",
    ...     structural_formula="...",
    ...     group="single",
    ...     additional_info="Highly fluorescent.",
    ... )
    >>> session.add(s)
    >>> session.commit()

    Loading via polymorphism:

    >>> mol = session.query(Molecule).filter_by(id=s.id).one()
    >>> type(mol)
    <class 'models.SingleMolecule'>
    """
    __tablename__ = "single"

    id = Column(Integer, ForeignKey("molecules.id", ondelete="CASCADE"),
                primary_key=True)

    additional_info = Column(Text)

    __mapper_args__ = {"polymorphic_identity": "single",}


class RP(Molecule):
    """
    Radical-pair molecule entry within the molecular hierarchy.

    This subclass of :class:`Molecule` represents a molecular system composed
    of two paramagnetic radical centres connected via a defined chemical
    linker.

    The class participates in the polymorphic SQLAlchemy inheritance structure
    via ``polymorphic_identity='rp'``. Any row in the base ``molecules`` table
    where ``group='rp'`` will be materialised as an :class:`RP` instance.

    Attributes
    ----------
    id : int
        Primary key referencing ``molecules.id``; cascades on deletion.
    radical_1 : av.Radicals
        Enumeration value describing the first radical centre.
    linker : av.Linker
        Enumeration defining the chemical linker bridging the two radicals.
    radical_2 : av.Radicals
        Enumeration value describing the second radical centre.

    Notes
    -----
    * The tablename is ``rp``.
    * Inherits all molecular base attributes from :class:`Molecule`, including
      ``name``, ``molecular_formula``, ``structural_formula``, timestamps, and
      the relationship to associated measurements.
    * Represents a *composite* molecular species with two radical sites, which
      may be identical or different.
    * All attributes specific to radical-pair composition are required
      (non-nullable).

    Examples
    --------
    Creating an RP molecule:

    >>> from models import RP
    >>> rp = RP(
    ...     name="TEMPO1–PH–TEMPO1",
    ...     molecular_formula="C26H44N2O4",
    ...     structural_formula="...",
    ...     group="rp",
    ...     radical_1="TEMPO1",
    ...     linker="PH",
    ...     radical_2="TEMPO1",
    ... )
    >>> session.add(rp)
    >>> session.commit()

    Loading via polymorphism:

    >>> mol = session.query(Molecule).filter_by(id=rp.id).one()
    >>> type(mol)
    <class 'models.RP'>
    """
    __tablename__ = "rp"

    id = Column(Integer, ForeignKey("molecules.id", ondelete="CASCADE"),
                primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "rp",}

    radical_1 = Column(SAEnum(av.Radicals), nullable=False)
    linker = Column(SAEnum(av.Linker), nullable=False)
    radical_2 = Column(SAEnum(av.Radicals), nullable=False)


class TDP(Molecule):
    """
    Triplet–doublet–pair (TDP) molecular entry in the polymorphic molecule
    hierarchy.

    This subclass of :class:`Molecule` represents a molecular system composed
    of a doublet spin centre connected via a defined chemical
    linker to a chromophore (triplet).

    The class participates in the SQLAlchemy polymorphic inheritance framework
    via ``polymorphic_identity='tdp'``. Any record in the ``molecules`` table
    with ``group='tdp'`` is instantiated as a :class:`TDP` object.

    Attributes
    ----------
    id : int
        Primary key referencing ``molecules.id``; cascades on deletion.
    doublet : av.Doublets
        Enumeration describing the radical (doublet) centre in the TDP system.
    linker : av.Linker
        Enumeration specifying the chemical linker connecting doublet and
        chromophoric units.
    chromophore : av.Chromophores
        Enumeration defining the chromophoric unit capable of forming a triplet
        excited state.

    Notes
    -----
    * The tablename is ``tdp``.
    * Inherits all common attributes from :class:`Molecule`, including
      ``name``, ``molecular_formula``, ``structural_formula``, timestamp fields,
      and relationships to associated measurements.
    * All TDP-specific attributes are required (non-nullable).

    Examples
    --------
    >>> from models import TDP
    >>> tdp = TDP(
    ...     name="PDI2-co-TEMPO1",
    ...     molecular_formula="C34H28N2O2",
    ...     structural_formula="...",
    ...     group="tdp",
    ...     doublet="TEMPO1"
    ...     linker="co"
    ...     chromophore="PDI2",
    ... )
    >>> session.add(tdp)
    >>> session.commit()

    Polymorphic loading:

    >>> mol = session.query(Molecule).get(tdp.id)
    >>> type(mol)
    <class 'models.TDP'>
    """
    __tablename__ = "tdp"

    id = Column(Integer, ForeignKey("molecules.id", ondelete="CASCADE"),
                primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "tdp",}

    doublet = Column(SAEnum(av.Doublets), nullable=False)
    linker = Column(SAEnum(av.Linker), nullable=False)
    chromophore = Column(SAEnum(av.Chromophores), nullable=False)



class TTP(Molecule):
    """
    Triplet–triplet–pair (TTP) molecular entry in the polymorphic molecule
    hierarchy.

    This subclass of :class:`Molecule` represents a molecular system composed
    of two chromophore triplet centres connected via a defined chemical
    linker.

    The class participates in the SQLAlchemy polymorphic inheritance framework
    via ``polymorphic_identity='ttp'``. Any database entry within the
    ``molecules`` table with ``group='ttp'`` is loaded as a :class:`TTP` object.

    Attributes
    ----------
    id : int
        Primary key referencing ``molecules.id``; cascades on deletion.
    triplet_1 : av.Chromophores
        Enumeration identifying the first chromophoric unit capable of forming
        a triplet excited state.
    linker : av.Linker
        Enumeration specifying the chemical linker that connects the two
        chromophores.
    triplet_2 : av.Chromophores
        Enumeration identifying the second chromophoric unit capable of forming
        a triplet excited state.

    Notes
    -----
    * The table name is ``ttp``.
    * Inherits all universal attributes from :class:`Molecule`, such as
      ``name``, ``molecular_formula``, ``structural_formula``, and timestamps.
    * All TTP-specific attributes are mandatory (non-nullable).

    Examples
    --------
    >>> from models import TTP
    >>> ttp = TTP(
    ...     name="PDI1-co-PDI2",
    ...     molecular_formula="C48H30O4",
    ...     structural_formula="...",
    ...     group="ttp",
    ...     triplet_1="PDI1",
    ...     linker="co",
    ...     triplet_2="PDI2",
    ... )
    >>> session.add(ttp)
    >>> session.commit()

    Polymorphic loading:

    >>> mol = session.query(Molecule).get(ttp.id)
    >>> type(mol)
    <class 'models.TTP'>
    """
    __tablename__ = "ttp"

    id = Column(Integer, ForeignKey("molecules.id", ondelete="CASCADE"),
                primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "ttp",}

    triplet_1= Column(SAEnum(av.Chromophores), nullable=False)
    linker = Column(SAEnum(av.Linker), nullable=False)
    triplet_2 = Column(SAEnum(av.Chromophores), nullable=False)
