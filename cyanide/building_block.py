import copy

import numpy as np

import ase
import ase.visualize

from .utils import read_budiling_block_xyz, covalent_neighbor_list
from .local_structure import LocalStructure

class BuildingBlock:
    def __init__(self, bb_file):
        self.atoms, cpi = read_budiling_block_xyz(bb_file)
        self.connection_point_indices = np.array(cpi)
        self._bonds = None

    def copy(self):
        return copy.deepcopy(self)

    def local_structure(self):
        connection_points = self.atoms[self.connection_point_indices].positions
        return LocalStructure(connection_points, self.connection_point_indices)

    def set_center(self, center):
        """
        Set center of connection points.
        """
        positions = self.atoms.positions
        # Move center to zero.
        positions = positions - self.center
        # Recenter by given value.
        positions = positions + center
        self.atoms.set_positions(positions)

    @property
    def center(self):
        center = np.mean(self.connection_points, axis=0)
        return center

    @property
    def connection_points(self):
        return self.atoms[self.connection_point_indices].positions

    @property
    def n_connection_potins(self):
        return len(self.connection_point_indices)

    @property
    def length(self):
        """
        distance between center and connecting point.
        """
        dists = self.connection_points - self.center
        norm = np.linalg.norm(dists, axis=1)
        # Return any norm.

        return norm[0]

    @property
    def is_edge(self):
        return self.n_connection_potins == 2

    @property
    def is_node(self):
        return not self.is_edge

    @property
    def bonds(self):
        if self._bonds is None:
            I, J, _ = covalent_neighbor_list(self.atoms)
            # Get i < j only.
            valid_indices = I < J
            I = I[valid_indices]
            J = J[valid_indices]

            self._bonds = np.array(list(zip(I, J)))

        return self._bonds

    @property
    def n_atoms(self):
        return len(self.atoms)

    def view(self):
        ase.visualize.view(self.atoms)